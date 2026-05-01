<!--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: Copyright the Vortex contributors
-->

# Vortex DataFusion CLI

This is a CLI tool to run use Vortex through the Apache DataFusion CLI tool, mostly intended for benchmarking it in benchmarking suites like [ClickBench](https://benchmark.clickhouse.com/).

In the future we hope we can minimize the amount of identical code, but for the time being this is a pragmatic solution.

## Versioning

Release tags use the format `<vortex-version>-<df-version>`, where `vortex-version` is the resolved `vortex-datafusion` crate version and `df-version` is the resolved `datafusion`/`datafusion-cli` crate version.

Merges to `main` create a tag only when `Cargo.lock` changes either of those resolved versions. Code, docs, or unrelated dependency changes still run CI, but do not create release tags.

[Renovate](https://docs.renovatebot.com/) updates Cargo manifests, `Cargo.lock`, and GitHub Actions workflow action versions. DataFusion and DataFusion CLI updates are grouped together so they continue to resolve to the same version.
