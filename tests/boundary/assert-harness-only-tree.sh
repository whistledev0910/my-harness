#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
tracked="$(mktemp)"
trap 'rm -f "$tracked"' EXIT
if ! git ls-files -z >"$tracked"; then
  echo "could not enumerate tracked paths" >&2
  exit 1
fi

assert_no_tracked_prefix() {
  local prefix="$1"
  if python3 - "$tracked" "$prefix" <<'PY'
import pathlib, sys
paths = pathlib.Path(sys.argv[1]).read_bytes().split(b"\0")
prefix = sys.argv[2].encode()
raise SystemExit(0 if any(path == prefix or path.startswith(prefix + b"/") for path in paths) else 1)
PY
  then
    echo "forbidden tracked path remains under $prefix" >&2
    exit 1
  fi
}

for prefix in \
  crates/harness-symphony \
  docs/stories/epics/E05-symphony-local-runner \
  docs/stories/epics/E06-symphony-review-sync \
  docs/stories/epics/E07-symphony-automation \
  docs/stories/epics/E08-symphony-web-ui-controller \
  .agents .codex .impeccable .harness/changesets
do
  assert_no_tracked_prefix "$prefix"
done

for file in \
  docs/SYMPHONY_SCOPE.md \
  docs/SYMPHONY_QUICKSTART.md \
  docs/product/symphony-web-ui-controller.md \
  docs/stories/US-046-first-class-symphony-codex-adapter.md
do
  if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
    echo "forbidden active Symphony product file remains tracked: $file" >&2
    exit 1
  fi
done

# Repository-harness has no active operation log, while installed consumers
# retain the generic opt-in rule allowing their own semantic changesets.
if ! grep -Fxq '!.harness/changesets/' .gitignore || \
   ! grep -Fxq '!.harness/changesets/*.changeset.jsonl' .gitignore; then
  echo "generic consumer changeset tracking exceptions are missing" >&2
  exit 1
fi

echo "repository-harness tracks no Symphony product or project-local tool tree"
