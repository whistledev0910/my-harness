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

release_tag=harness-cli-v0.1.14
release_commit=d2f89eeabe8d01df95fd19cd6ba981b01a71730f
test "$(git ls-remote origin "refs/tags/${release_tag}^{}" | awk '{print $1}')" = "$release_commit"
test "$(gh run view 29177994849 --repo hoangnb24/repository-harness --json conclusion --jq .conclusion)" = success

release_dir=$(mktemp -d)
trap 'rm -rf "$release_dir"' EXIT
gh release download "$release_tag" --repo hoangnb24/repository-harness \
  --dir "$release_dir" --pattern 'harness-cli-*'
test "$(find "$release_dir" -maxdepth 1 -type f | wc -l | tr -d ' ')" = 10
(
  cd "$release_dir"
  for checksum in *.sha256; do
    shasum -a 256 -c "$checksum" >/dev/null
  done
)
while read -r expected artifact; do
  test "$(awk '{print $1}' "$release_dir/${artifact}.sha256")" = "$expected"
done <<'EOF'
0adcd5360cd636c189fe0cd958e5b73261f7012a4e43631f08c61269c785caf9 harness-cli-macos-arm64
d0ee0b6b9f702eb87824e96b42d7a8382012b542a076e8ce2d0b1bb8d6201168 harness-cli-macos-x64
8828d624075fbae2f44b6f57ac651bdacb2e7c60ed0cc15853b9481b3edf0161 harness-cli-linux-arm64
d2551d32490d0af78f8eb387d8854771ebfcde2260b068539384592668cc54a6 harness-cli-linux-x64
abd5a4176d52b3576c66932f44f377d2667fba409011de145044f425fd0a82ca harness-cli-windows-x64.exe
EOF

case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) released_artifact=harness-cli-macos-arm64 ;;
  Darwin-x86_64) released_artifact=harness-cli-macos-x64 ;;
  Linux-aarch64) released_artifact=harness-cli-linux-arm64 ;;
  Linux-x86_64) released_artifact=harness-cli-linux-x64 ;;
  *) released_artifact= ;;
esac
if [ -n "$released_artifact" ]; then
  chmod +x "$release_dir/$released_artifact"
  bash tests/protocol/smoke-native-artifact.sh "$release_dir/$released_artifact"
fi
git diff --check

echo "US-092 protocol-v1 release verification passed"
