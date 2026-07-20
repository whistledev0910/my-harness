# Scripts

This directory contains harness automation tools.

## Harness CLI

The Rust Harness CLI is the primary interface for the durable layer. Installed
projects use the prebuilt binary at `scripts/bin/harness-cli` on macOS/Linux or
`scripts/bin/harness-cli.exe` on Windows for normal Harness work.

```bash
scripts/bin/harness-cli init          # Create the database
scripts/bin/harness-cli intake ...    # Record a feature intake classification
scripts/bin/harness-cli story ...     # Add or update a story (test matrix row)
scripts/bin/harness-cli story update --id US-001 --unit 1 --integration 1 --e2e 0 --platform 0
scripts/bin/harness-cli story verify US-001  # Run the story's verify_command
scripts/bin/harness-cli decision ...  # Add a decision or run its verification
scripts/bin/harness-cli backlog ...   # Add or close a backlog item
scripts/bin/harness-cli trace ...     # Record and auto-score an agent execution trace
scripts/bin/harness-cli score-trace   # Score a trace against TRACE_SPEC.md tiers
scripts/bin/harness-cli query ...     # Query harness data, including backlog --open/--closed
scripts/bin/harness-cli query matrix --numeric  # Show proof flags as 1/0
scripts/bin/harness-cli migrate       # Apply pending schema migrations
scripts/bin/harness-cli --version     # Print the installed CLI version
```

Run `scripts/bin/harness-cli help` or `scripts/bin/harness-cli query help` for
full usage. On Windows, use the same commands through
`.\scripts\bin\harness-cli.exe`.

Proof flags on `story update` are numeric booleans: use `1` for yes and `0` for
no. `story verify <id>` runs the configured `verify_command`; it does not accept
proof flags. Configure the command with `story add/update --verify`, run
`story verify <id>`, then update proof flags with `story update`.

Backlog `--risk` uses Harness lanes, not severity words: use `tiny`, `normal`,
or `high-risk`. Use `tiny` instead of `low`. `query matrix` defaults to
human-readable `yes`/`no`; use `query matrix --numeric` when copying values into
`story update`.

The schema lives in `scripts/schema/` and is version-controlled. The database
file (`harness.db`) is `.gitignore`d.

Requires: the prebuilt Rust CLI at `scripts/bin/harness-cli` on macOS/Linux or
`scripts/bin/harness-cli.exe` on Windows.

Direct database inspection may still use SQLite tools, but normal Harness use
should go through the Rust CLI.

### Rust CLI Commands

Current migrated commands:

```bash
scripts/bin/harness-cli init
scripts/bin/harness-cli migrate
scripts/bin/harness-cli import brownfield
scripts/bin/harness-cli intake ...
scripts/bin/harness-cli story add ...
scripts/bin/harness-cli story update ...
scripts/bin/harness-cli story verify ...
scripts/bin/harness-cli decision add ...
scripts/bin/harness-cli decision verify ...
scripts/bin/harness-cli backlog add ...
scripts/bin/harness-cli backlog close ...
scripts/bin/harness-cli trace ...
scripts/bin/harness-cli score-trace
scripts/bin/harness-cli query matrix
scripts/bin/harness-cli query backlog
scripts/bin/harness-cli query decisions
scripts/bin/harness-cli query intakes
scripts/bin/harness-cli query traces
scripts/bin/harness-cli query friction
scripts/bin/harness-cli query stats
scripts/bin/harness-cli query sql ...
```

`scripts/bin/harness-cli import brownfield` seeds or refreshes the durable database
from existing Harness v0 markdown in `docs/TEST_MATRIX.md`,
`docs/decisions/`, and `docs/HARNESS_BACKLOG.md`. This keeps already-installed
Harness repos on the Rust CLI path without losing their populated operating
docs.

## Installer

The default installer is docs-only and safe for an existing repository. It
copies Harness documentation into `.harness/docs/`, writes
`.harness/README.md` and `.harness/VERSION`, and creates or refreshes only the
marked Harness block in `AGENTS.md`. Existing project files under `docs/`,
`scripts/`, and the rest of `AGENTS.md` remain untouched.

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --dry-run
```

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --yes
```

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --directory /path/to/project --yes
```

The installer supports `--directory`, `--dry-run`, `--yes`, and `--help`.
`HARNESS_REF` pins the downloaded branch or tag, and `HARNESS_REPOSITORY`
selects a fork. Re-running it updates the vendored docs and keeps exactly one
Harness block in `AGENTS.md`.

The Rust CLI, database, dashboard, and helper scripts are source-repository
tools and are not part of the default installed payload. The installer test
runs without network access:

```bash
scripts/test-install-harness.sh
```

## Schema Migrations

Migration files live under `scripts/schema/` and are named `NNN-description.sql`
where `NNN` is a zero-padded version number. Run `scripts/bin/harness-cli migrate` to
apply pending migrations.

## Future Command Contract

Expected future checks:

```text
validate:quick
  format, lint, typecheck, unit tests, architecture check

test:integration
  backend contract and integration checks

test:e2e
  user-visible end-to-end flows

test:platform
  platform shell smoke checks, if the project has a native shell

test:release
  full suite, log checks, and performance smoke
```

## Release Packaging

Build the current-platform Rust CLI release artifact from the source repo:

```bash
scripts/build-harness-cli-release.sh
```

The script writes `dist/harness-cli-<platform>` plus `.sha256` checksums. The
Windows artifact includes the `.exe` suffix. Supported labels are:

- `macos-arm64`
- `macos-x64`
- `linux-x64`
- `linux-arm64`
- `windows-x64`

For cross-compilation, pass a Cargo target triple:

```bash
scripts/build-harness-cli-release.sh --target x86_64-unknown-linux-gnu
```

GitHub releases are produced by
`.github/workflows/harness-cli-release.yml`. Push a tag matching `v*` or
`harness-cli-v*` to run the verification job, build all supported targets on
native hosted runners, and upload these release assets:

- `harness-cli-macos-arm64`
- `harness-cli-macos-arm64.sha256`
- `harness-cli-macos-x64`
- `harness-cli-macos-x64.sha256`
- `harness-cli-linux-x64`
- `harness-cli-linux-x64.sha256`
- `harness-cli-linux-arm64`
- `harness-cli-linux-arm64.sha256`
- `harness-cli-windows-x64.exe`
- `harness-cli-windows-x64.exe.sha256`

Merged PRs are handled by `.github/workflows/post-merge-maintenance.yml`. The
workflow always prepends a PR summary to `CHANGELOG.md`. If the merged PR
changed `crates/harness-cli/`, `scripts/schema/`, Cargo metadata, or
`scripts/build-harness-cli-release.sh`, it also increments the CLI patch
version, updates `scripts/harness-cli-release-tag`, creates a matching
`harness-cli-v*` tag, and calls the reusable Harness CLI release workflow for
the tagged ref.
