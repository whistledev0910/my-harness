#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../.." && pwd)
verifier="$root/docs/stories/epics/E11-symphony-repository-separation/evidence/verify-target-receipt.sh"
for story in US-093 US-094 US-095 US-096; do "$verifier" "$story" >/dev/null; done
if "$verifier" US-097 >/dev/null 2>&1; then echo "unsupported receipt passed" >&2; exit 1; fi
temp=$(mktemp -d)
trap 'rm -rf "$temp"' EXIT
cp -R "$root/docs/stories/epics/E11-symphony-repository-separation/evidence" "$temp/evidence"
printf ' ' >>"$temp/evidence/receipts/US-093.json"
if (cd "$temp/evidence/receipts" && shasum -a 256 -c US-093.json.sha256 >/dev/null 2>&1); then
  echo "tampered receipt passed checksum validation" >&2
  exit 1
fi
echo "historical receipt verifier tests passed"
