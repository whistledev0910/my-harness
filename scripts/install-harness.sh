#!/usr/bin/env bash

set -euo pipefail

REPOSITORY="${HARNESS_REPOSITORY:-whistledev0910/my-harness}"
REF="${HARNESS_REF:-main}"
TARGET_DIR="$(pwd)"
YES=false
DRY_RUN=false
HARNESS_DIR=".harness"
BEGIN_MARKER='<!-- HARNESS:BEGIN -->'
END_MARKER='<!-- HARNESS:END -->'

usage() {
  cat <<'EOF'
Usage: install-harness.sh [--directory PATH] [--dry-run] [--yes]

Installs the docs-only Harness into .harness/ and adds an idempotent block to
AGENTS.md. Existing project docs, scripts, and agent instructions are kept.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --directory)
      [ "$#" -ge 2 ] || { echo "error: --directory requires a path" >&2; exit 2; }
      TARGET_DIR="$2"
      shift
      ;;
    --directory=*) TARGET_DIR="${1#*=}" ;;
    --dry-run) DRY_RUN=true ;;
    --yes) YES=true ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

[ -d "$TARGET_DIR" ] || { echo "error: target directory does not exist: $TARGET_DIR" >&2; exit 1; }
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

if [ "$DRY_RUN" = true ]; then
  echo "Would install Harness docs into $TARGET_DIR/$HARNESS_DIR"
  echo "Would create or update only the marked Harness block in $TARGET_DIR/AGENTS.md"
  exit 0
fi

if [ "$YES" = false ]; then
  printf 'Install docs-only Harness into %s/%s? (y/N) ' "$TARGET_DIR" "$HARNESS_DIR"
  read -r answer
  case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Installation cancelled."; exit 1 ;;
  esac
fi

AGENTS_FILE="$TARGET_DIR/AGENTS.md"
if [ -e "$AGENTS_FILE" ] && {
  grep -Fqx "$BEGIN_MARKER" "$AGENTS_FILE" || grep -Fqx "$END_MARKER" "$AGENTS_FILE"
}; then
  if ! awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" '
    $0 == begin { begin_count++; begin_line=NR }
    $0 == end { end_count++; end_line=NR }
    END { exit !(begin_count == 1 && end_count == 1 && begin_line < end_line) }
  ' "$AGENTS_FILE"; then
    echo "error: AGENTS.md has a malformed Harness block; refusing to install" >&2
    exit 1
  fi
fi

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT
SOURCE_DIR="${HARNESS_SOURCE_DIR:-$TEMP_DIR/source}"

if [ -z "${HARNESS_SOURCE_DIR:-}" ]; then
  archive="$TEMP_DIR/harness.tar.gz"
  curl_args=(-fsSL)
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    curl_args+=(-H "Authorization: Bearer $GITHUB_TOKEN")
  elif [ -n "${GH_TOKEN:-}" ]; then
    curl_args+=(-H "Authorization: Bearer $GH_TOKEN")
  fi
  curl "${curl_args[@]}" "https://github.com/$REPOSITORY/archive/$REF.tar.gz" -o "$archive"
  mkdir -p "$SOURCE_DIR"
  tar -xzf "$archive" -C "$SOURCE_DIR" --strip-components=1
fi

[ -d "$SOURCE_DIR/docs" ] || { echo "error: Harness docs not found in $SOURCE_DIR" >&2; exit 1; }

mkdir -p "$TARGET_DIR/$HARNESS_DIR/docs"
cp -R "$SOURCE_DIR/docs/." "$TARGET_DIR/$HARNESS_DIR/docs/"
printf '%s\n' "$REF" > "$TARGET_DIR/$HARNESS_DIR/VERSION"

cat > "$TARGET_DIR/$HARNESS_DIR/README.md" <<'EOF'
# Harness

This is a docs-only Harness installation. Project-specific instructions and
existing project conventions take precedence over generic Harness guidance.

- Harness references beginning with `docs/` resolve under `.harness/docs/`.
- Harness CLI, SQLite, dashboard, and helper scripts are not installed.
- Skip CLI-only recording steps; use the project's existing issue, decision,
  documentation, and validation systems instead.
EOF

BLOCK_FILE="$TEMP_DIR/agents-block.md"
cat > "$BLOCK_FILE" <<'EOF'
<!-- HARNESS:BEGIN -->
## Harness

This repo uses the docs-only Harness. Project-specific instructions take
precedence. Before work, read:

- `README.md` when present
- `.harness/README.md`
- `.harness/docs/HARNESS.md`
- `.harness/docs/FEATURE_INTAKE.md`
- `.harness/docs/ARCHITECTURE.md`
- `.harness/docs/CONTEXT_RULES.md`

Do not use Harness CLI commands unless the project separately installs the CLI.
<!-- HARNESS:END -->
EOF

if [ ! -e "$AGENTS_FILE" ]; then
  cp "$BLOCK_FILE" "$AGENTS_FILE"
elif grep -Fqx "$BEGIN_MARKER" "$AGENTS_FILE" || grep -Fqx "$END_MARKER" "$AGENTS_FILE"; then
  UPDATED_FILE="$TEMP_DIR/AGENTS.md"
  awk -v begin="$BEGIN_MARKER" -v end="$END_MARKER" -v block_file="$BLOCK_FILE" '
    $0 == begin {
      while ((getline line < block_file) > 0) print line
      close(block_file)
      inside=1
      next
    }
    $0 == end { inside=0; next }
    !inside { print }
  ' "$AGENTS_FILE" > "$UPDATED_FILE"
  cp "$UPDATED_FILE" "$AGENTS_FILE"
else
  [ ! -s "$AGENTS_FILE" ] || printf '\n' >> "$AGENTS_FILE"
  cat "$BLOCK_FILE" >> "$AGENTS_FILE"
fi

echo "Harness docs installed in $TARGET_DIR/$HARNESS_DIR"
echo "Existing project docs, scripts, and non-Harness instructions were left in place."
