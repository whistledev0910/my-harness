# Overview

## Current Behavior

Repository-harness contains the Symphony crate, product docs, E05-E08 backlog,
Web/Electron tooling, vendored Impeccable skill, Codex hook/skill, UI ignore
rules, mixed root manifests, and release/test workflows. Some generic core docs
and stories also use Symphony-specific names or proof commands.

## Target Behavior

After the standalone target release candidate and history partition pass,
repository-harness contains one product: the reusable Harness template and CLI.
Historical references are retained only in the approved allowlist. Fresh
installs are internally complete and contain no Symphony instructions they
cannot execute.

## Affected Users

- Harness users installing the template.
- Harness CLI maintainers and release automation.
- Agents selecting work from source docs and durable state.

## Affected Product Docs

- Root and docs READMEs.
- Harness component inventory and active epic index.
- E04, E09, E10, US-072, and US-081 mixed evidence.
- Installer/release documentation.

## Acceptance Criteria

- `crates/harness-symphony/**` is removed from repository-harness only after the
  `US-096` target candidate is recorded.
- Root Cargo workspace has exactly `crates/harness-cli`; lockfile is regenerated
  and no Symphony package/dependencies remain.
- Symphony scope, quickstart, product contract, US-046, and E05-E08 active story
  trees leave the source after their target counterparts and provenance verify.
- E04 remains in Harness but is renamed/generalized as isolated durable state
  and semantic replay work rather than a Symphony prerequisite.
- Schema 007/008 and retained generic features use consumer-neutral comments and
  docs.
- Mixed E09/E10/US-072/US-081 verification commands no longer invoke Symphony,
  Web UI, Electron, or Impeccable.
- `.agents/**` and `.codex/**` are untracked from repository-harness; no core
  command references local `.impeccable/**`. The ignored personal directory is
  inventoried here and removed in the reviewed local-state cleanup at `US-100`,
  rather than being silently deleted by a source-removal commit.
- Root/documentation indexes no longer advertise local Symphony commands or
  link to removed files. An optional external product link, if kept, points to
  the released target and is clearly non-core.
- `.gitignore` and installer payload contain only generic Harness runtime/build
  entries; fresh installs do not receive Symphony/Web/Electron ignores. The
  generic exception/template rule that permits a consumer to commit its own
  `.harness/changesets/*.jsonl` remains even though repository-harness has no
  live files there.
- CLI release CI selects Harness CLI tests explicitly, and Symphony dependency
  changes can no longer trigger a Harness release.
- Post-merge changelog generation caps or summarizes large changed-file lists
  before the bulk removal is merged.
- A boundary check rejects active Symphony references outside decision `0009`,
  completed E11/history/changelog allowlists.
- After all four target receipts have completed their source proxies, move the
  immutable receipts plus a local fail-closed historical verifier under E11's
  evidence allowlist, update the completed proxy verify commands through the
  CLI, prove `story verify-all`, and remove the temporary root
  `scripts/verify-e11-external-gate.sh`. No installed template payload receives
  this migration-only verifier.
- `git ls-files` returns no active Symphony source/product path, `.agents`,
  `.codex`, `.impeccable`, or `.harness/changesets` path.
- A fresh installed consumer can generate and `git add` one semantic changeset;
  root repository-harness itself still tracks none.
- Ignored worktrees/runs are not deleted in this story.

## Non-Goals

- Remove generic Harness capabilities that Symphony first exercised.
- Rewrite dated changelog/PR history to pretend Symphony never existed.
- Prune local Git worktrees or branches.
- Publish either product release.
