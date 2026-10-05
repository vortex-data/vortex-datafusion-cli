<!--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: Copyright the Vortex contributors
-->

# Vortex DataFusion CLI

This is a CLI tool to run use Vortex through the Apache DataFusion CLI tool, mostly intended for benchmarking it in benchmarking suites like [ClickBench](https://benchmark.clickhouse.com/).

In the future we hope we can minimize the amount of identical code, but for the time being this is a pragmatic solution.

## Download

Download a prebuilt binary from the [latest release](https://github.com/vortex-data/vortex-datafusion-cli/releases/latest). No Rust toolchain is needed.

| Platform | Archive |
| --- | --- |
| Linux x86-64 (Ubuntu 22.04 or newer) | `vortex-datafusion-cli-x86_64-unknown-linux-gnu.tar.gz` |
| macOS Apple Silicon (macOS 14 or newer) | `vortex-datafusion-cli-aarch64-apple-darwin.tar.gz` |

The Linux binary is dynamically linked and targets the Ubuntu 22.04 runtime libraries (including glibc 2.35). Other Linux distributions need compatible runtime libraries; Alpine/musl is not supported by this build.

For example, on Linux x86-64:

```sh
target=x86_64-unknown-linux-gnu
archive="vortex-datafusion-cli-${target}"
base=https://github.com/vortex-data/vortex-datafusion-cli/releases/latest/download
curl -fLO "${base}/${archive}.tar.gz"
curl -fLO "${base}/${archive}.tar.gz.sha256"
sha256sum -c "${archive}.tar.gz.sha256"
tar -xzf "${archive}.tar.gz"
mkdir -p "$HOME/.local/bin"
install -m 755 "${archive}/vortex-datafusion-cli" "$HOME/.local/bin/vortex-datafusion-cli"
export PATH="$HOME/.local/bin:$PATH"
vortex-datafusion-cli --version
```

On macOS, set `target=aarch64-apple-darwin` and use `shasum -a 256 -c` instead of `sha256sum -c`. Add `$HOME/.local/bin` to your shell's startup configuration to keep the command on `PATH` in new sessions.

For reproducible benchmarks, download a specific [release](https://github.com/vortex-data/vortex-datafusion-cli/releases) by replacing `releases/latest/download` in `base` with `releases/download/<tag>`.

## Versioning

Release tags use the format `<vortex-version>-<df-version>`, where `vortex-version` is the resolved `vortex-datafusion` crate version and `df-version` is the resolved `datafusion`/`datafusion-cli` crate version.

Pushes to `main` create the current tag if it does not already exist. Later merges to `main` create a new tag only when `Cargo.lock` changes either of those resolved versions. Code, docs, or unrelated dependency changes still run CI, but do not create release tags once the current tag exists.

After CI passes on `main`, the workflow builds binaries from the current tag's commit and publishes a GitHub Release with both archives and their SHA-256 checksums. An existing tag without a published release is also packaged, so the first release does not require a dependency update. Published releases are left unchanged. Failed builds or draft uploads can be retried by rerunning the workflow; publication waits for both platforms to succeed. Pull requests build and smoke-test the same archives without publishing them.

[Renovate](https://docs.renovatebot.com/) updates Cargo manifests, `Cargo.lock`, and GitHub Actions workflow action versions. Vortex, DataFusion, and DataFusion CLI updates are grouped together, including major upgrades, so their integration uses compatible DataFusion versions.
