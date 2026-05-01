#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright the Vortex contributors

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("version_pair.py")
FIXTURES = Path(__file__).parent / "fixtures" / "version_pair"


class VersionPairCliTest(unittest.TestCase):
    def test_tag_and_mismatched_datafusion_versions(self) -> None:
        result = self.run_script("tag", "--lockfile", fixture("current.lock"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.69.0-53.1.0")

        result = self.run_script("tag", "--lockfile", fixture("mismatched.lock"))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("resolves datafusion 53.1.0", result.stderr)
        self.assertIn("datafusion-cli 54.0.0", result.stderr)

    def test_changed_lockfiles(self) -> None:
        result = self.run_script(
            "changed",
            "--old",
            fixture("current.lock"),
            "--new",
            fixture("current.lock"),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no release needed", result.stdout)

        with tempfile.NamedTemporaryFile() as output:
            result = self.run_script(
                "changed",
                "--old",
                fixture("current.lock"),
                "--new",
                fixture("both-changed.lock"),
                "--github-output",
                output.name,
            )
            output.seek(0)
            github_output = output.read().decode("utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("release needed", result.stdout)
        self.assertIn("release_needed=true\n", github_output)
        self.assertIn("old_tag=0.69.0-53.1.0\n", github_output)
        self.assertIn("new_tag=0.70.0-54.0.0\n", github_output)
        self.assertIn("changes=vortex-datafusion,datafusion/datafusion-cli\n", github_output)

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            text=True,
            capture_output=True,
        )


def fixture(name: str) -> str:
    return str(FIXTURES / name)


if __name__ == "__main__":
    unittest.main()
