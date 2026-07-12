#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
manifest="$root/scripts/harness-install-files.txt"
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
assets="$temp/assets/harness-cli-v0.1.14"
consumer="$temp/consumer"
platform=fixture-platform
mkdir -p "$assets" "$consumer"

# Both platform installers must consume the one canonical payload declaration.
[[ "$(grep -Fc 'PAYLOAD_MANIFEST="scripts/harness-install-files.txt"' "$root/scripts/install-harness.sh")" == 1 ]]
[[ "$(grep -Fc '$script:PayloadManifest = "scripts/harness-install-files.txt"' "$root/scripts/install-harness.ps1")" == 1 ]]

python3 - "$root" "$manifest" <<'PY'
import pathlib, sys
root, manifest = map(pathlib.Path, sys.argv[1:])
seen = set()
for number, raw in enumerate(manifest.read_text().splitlines(), 1):
    value = raw.strip()
    if not value or value.startswith("#"):
        continue
    if value.startswith("/") or ".." in pathlib.PurePosixPath(value).parts:
        raise SystemExit(f"unsafe manifest path at line {number}: {value}")
    if value in seen:
        raise SystemExit(f"duplicate manifest path: {value}")
    seen.add(value)
    if not (root / value).is_file():
        raise SystemExit(f"missing manifest source: {value}")
PY

printf '%s\n' '#!/usr/bin/env sh' 'exit 0' >"$assets/harness-cli-$platform"
chmod 755 "$assets/harness-cli-$platform"
(cd "$assets" && shasum -a 256 "harness-cli-$platform" >"harness-cli-$platform.sha256")
HARNESS_CLI_BASE_URL="file://$assets" \
HARNESS_CLI_PLATFORM="$platform" \
HARNESS_CLI_RELEASE_TAG=harness-cli-v0.1.14 \
  "$root/scripts/install-harness.sh" --directory "$consumer" --yes >/dev/null

python3 - "$consumer" <<'PY'
import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
pattern = re.compile(r"!?(?:\[[^]]*\])\(([^)]+)\)")
errors = []
for document in root.rglob("*.md"):
    for target in pattern.findall(document.read_text(errors="replace")):
        target = target.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        relative = target.split("#", 1)[0]
        resolved = (document.parent / relative).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{document.relative_to(root)}: link escapes install root: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{document.relative_to(root)}: missing local link: {target}")
if errors:
    raise SystemExit("\n".join(errors))
PY

while IFS= read -r relative; do
  case "$relative" in ''|'#'*) continue ;; esac
  [[ -f "$consumer/$relative" ]] || { echo "installed payload missing $relative" >&2; exit 1; }
done <"$manifest"

echo "installer manifest parity and fresh-install link checks passed"
