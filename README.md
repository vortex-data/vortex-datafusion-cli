<--
SPDX-License-Identifier: Apache-2.0
SPDX-FileCopyrightText: Copyright the Vortex contributors
-->

# Vortex DataFusion CLI

This is a CLI tool to run use Vortex through the Apache DataFusion CLI tool, mostly intended for benchmarking it in benchmarking suites like [ClickBench](https://benchmark.clickhouse.com/).

In the future we hope we can minimize the amount of identical code, but for the time being this is a pragmatic solution.

## Versioning

For each update of Apache DataFusion or Vortex, we'll want to create a new tag `<vortex-version>-<df-version>` so we can check every support version combination of both tools.
