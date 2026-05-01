#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright the Vortex contributors

"""Compute release tags from resolved Cargo dependency versions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib


DATAFUSION = "datafusion"
DATAFUSION_CLI = "datafusion-cli"
VORTEX_DATAFUSION = "vortex-datafusion"


class VersionPairError(ValueError):
    """Raised when a lockfile cannot produce one valid release version pair."""


@dataclass(frozen=True)
class VersionPair:
    vortex_datafusion: str
    datafusion: str

    @property
    def tag(self) -> str:
        return f"{self.vortex_datafusion}-{self.datafusion}"


@dataclass(frozen=True)
class VersionChange:
    old: VersionPair
    new: VersionPair

    @property
    def changed_components(self) -> tuple[str, ...]:
        changed: list[str] = []
        if self.old.vortex_datafusion != self.new.vortex_datafusion:
            changed.append(VORTEX_DATAFUSION)
        if self.old.datafusion != self.new.datafusion:
            changed.append(f"{DATAFUSION}/{DATAFUSION_CLI}")
        return tuple(changed)

    @property
    def release_needed(self) -> bool:
        return bool(self.changed_components)


def read_version_pair(lockfile: Path) -> VersionPair:
    try:
        with lockfile.open("rb") as lockfile_handle:
            cargo_lock = tomllib.load(lockfile_handle)
    except OSError as error:
        raise VersionPairError(f"failed to read {lockfile}: {error}") from error
    except tomllib.TOMLDecodeError as error:
        raise VersionPairError(f"failed to parse {lockfile}: {error}") from error

    packages = cargo_lock.get("package")
    if not isinstance(packages, list):
        raise VersionPairError(f"{lockfile} does not contain any [[package]] entries")

    datafusion_version = _single_resolved_version(packages, DATAFUSION, lockfile)
    datafusion_cli_version = _single_resolved_version(packages, DATAFUSION_CLI, lockfile)
    vortex_datafusion_version = _single_resolved_version(
        packages, VORTEX_DATAFUSION, lockfile
    )

    if datafusion_version != datafusion_cli_version:
        raise VersionPairError(
            f"{lockfile} resolves {DATAFUSION} {datafusion_version} but "
            f"{DATAFUSION_CLI} {datafusion_cli_version}"
        )

    return VersionPair(
        vortex_datafusion=vortex_datafusion_version,
        datafusion=datafusion_version,
    )


def _single_resolved_version(
    packages: list[object], package_name: str, lockfile: Path
) -> str:
    versions = {
        package.get("version")
        for package in packages
        if isinstance(package, dict) and package.get("name") == package_name
    }
    versions.discard(None)

    if not versions:
        raise VersionPairError(f"{lockfile} does not resolve {package_name}")
    if len(versions) > 1:
        versions_display = ", ".join(sorted(str(version) for version in versions))
        raise VersionPairError(
            f"{lockfile} resolves multiple {package_name} versions: {versions_display}"
        )

    version = versions.pop()
    if not isinstance(version, str):
        raise VersionPairError(f"{lockfile} has a non-string version for {package_name}")
    return version


def compare_lockfiles(old_lockfile: Path, new_lockfile: Path) -> VersionChange:
    return VersionChange(
        old=read_version_pair(old_lockfile),
        new=read_version_pair(new_lockfile),
    )


def write_github_output(path: Path, change: VersionChange) -> None:
    release_needed = "true" if change.release_needed else "false"
    changes = ",".join(change.changed_components)
    with path.open("a", encoding="utf-8") as output:
        output.write(f"release_needed={release_needed}\n")
        output.write(f"old_tag={change.old.tag}\n")
        output.write(f"new_tag={change.new.tag}\n")
        output.write(f"changes={changes}\n")


def print_change(change: VersionChange) -> None:
    if not change.release_needed:
        print(f"no release needed: {change.new.tag}")
        return

    changes = ", ".join(change.changed_components)
    print(f"release needed: {change.old.tag} -> {change.new.tag} ({changes})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute release tags from resolved Cargo dependency versions."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    tag_parser = subcommands.add_parser("tag", help="print the release tag")
    tag_parser.add_argument(
        "--lockfile",
        type=Path,
        default=Path("Cargo.lock"),
        help="Cargo.lock path to inspect",
    )

    changed_parser = subcommands.add_parser(
        "changed", help="compare two lockfiles for release-relevant version changes"
    )
    changed_parser.add_argument("--old", type=Path, required=True, help="old Cargo.lock")
    changed_parser.add_argument(
        "--new",
        type=Path,
        default=Path("Cargo.lock"),
        help="new Cargo.lock",
    )
    changed_parser.add_argument(
        "--github-output",
        type=Path,
        help="append GitHub Actions outputs to this file",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "tag":
            print(read_version_pair(args.lockfile).tag)
            return 0

        if args.command == "changed":
            change = compare_lockfiles(args.old, args.new)
            print_change(change)
            if args.github_output is not None:
                write_github_output(args.github_output, change)
            return 0

    except VersionPairError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
