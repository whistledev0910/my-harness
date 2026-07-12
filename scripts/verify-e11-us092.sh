#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

cargo fmt --all -- --check
cargo test -p harness-cli --locked
cargo clippy -p harness-cli --all-targets --locked -- -D warnings
cargo build -p harness-cli --locked
bash tests/protocol/smoke-native-artifact.sh "${E11_US092_ARTIFACT:-target/debug/harness-cli}"
bash scripts/test-install-harness-cli-upgrade.sh
git diff --check

echo "US-092 pre-release verification passed"
