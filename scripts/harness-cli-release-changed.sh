#!/usr/bin/env bash
set -euo pipefail

# Exit successfully only when a changed path can alter the published Harness
# CLI binary or its schema/release packaging. The root workspace contains only
# harness-cli, so its manifest and lockfile are part of the published binary.
grep -Eq '^(crates/harness-cli/|scripts/schema/|scripts/build-harness-cli-release\.sh$|Cargo\.toml$|Cargo\.lock$)'
