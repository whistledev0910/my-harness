#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
allowlist="$root/tests/boundary/symphony-history-allowlist.tsv"
matches=$(mktemp)
trap 'rm -f "$matches"' EXIT
cd "$root"
while IFS= read -r -d '' path; do
  test -f "$path" || continue
  if grep -Iqi -E 'symphony|harness-symphony|\.symphony' "$path"; then
    printf '%s\n' "$path"
  fi
done < <(git ls-files -co --exclude-standard -z) | LC_ALL=C sort -u >"$matches"

while IFS= read -r path; do
  test -n "$path" || continue
  if ! awk -F '\t' -v path="$path" '
    $1 == "exact" && $2 == path { found=1 }
    $1 == "prefix" && (path == $2 || index(path, $2 "/") == 1) { found=1 }
    END { exit found ? 0 : 1 }
  ' "$allowlist"; then
    echo "unclassified active product reference: $path" >&2
    exit 1
  fi
done <"$matches"

while IFS=$'\t' read -r match path class reason; do
  [[ -n "$match" && "$match" != \#* ]] || continue
  case "$class" in historical_allowed|generic_origin_note|migration_plan) ;; *) echo "invalid allowlist class: $class" >&2; exit 1;; esac
  case "$match" in
    exact) grep -Fxq "$path" "$matches" || { echo "stale exact allowlist entry: $path" >&2; exit 1; } ;;
    prefix) grep -Eq "^${path//./\\.}(/|$)" "$matches" || { echo "stale prefix allowlist entry: $path" >&2; exit 1; } ;;
    *) echo "invalid allowlist match type: $match" >&2; exit 1;;
  esac
done <"$allowlist"

echo "all product-name references are explicitly historical or external-origin notes"
