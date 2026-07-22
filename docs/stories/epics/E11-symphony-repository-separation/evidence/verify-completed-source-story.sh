#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 1 ]] || { echo "usage: $0 <US-089|US-090|US-091|US-092|US-097>" >&2; exit 2; }
story=$1
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
case "$story" in
  US-089)
    file="docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence/source.json"
    marker="6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9" ;;
  US-090)
    file="docs/stories/epics/E11-symphony-repository-separation/US-090-provenance-preserving-symphony-bootstrap/validation.md"
    marker="5db694c8fd43a7d0e34bd9eaf9030d18b856f2b5" ;;
  US-091)
    file="docs/stories/epics/E11-symphony-repository-separation/US-091-standalone-symphony-workspace.md"
    marker="61e92c2a73ba3381e0d50b11509ba0eeed079bc9" ;;
  US-092)
    file="docs/stories/epics/E11-symphony-repository-separation/US-092-machine-readable-harness-orchestration-contract/validation.md"
    marker="harness-cli-v0.1.14" ;;
  US-097)
    summary="docs/provenance/e11-us097-epoch-summary.json"
    sidecar="$summary.sha256"
    git -C "$root" ls-files --error-unmatch -- "$summary" "$sidecar" >/dev/null
    (cd "$root/$(dirname "$summary")" && shasum -a 256 -c "$(basename "$sidecar")" >/dev/null)
    echo "completed source story evidence verified: $story"
    exit 0 ;;
  *) echo "unsupported completed source story: $story" >&2; exit 2 ;;
esac
git -C "$root" ls-files --error-unmatch -- "$file" >/dev/null
grep -Fq "$marker" "$root/$file" || { echo "historical marker missing for $story" >&2; exit 1; }
echo "completed source story evidence verified: $story"
