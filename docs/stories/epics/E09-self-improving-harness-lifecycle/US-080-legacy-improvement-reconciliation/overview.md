# Overview

## Status

implemented

## Lane

high-risk

## Product Contract

Existing Harness improvement rows enter the new lifecycle only when stable
identity can be derived deterministically; ambiguous and historical records
remain untouched and explainable.

## Current Behavior

Existing backlog rows predate stable proposal keys and occurrence uids. Known
generated rows such as backlog #6 and #7 can be associated with current proposal
patterns, while manual or similarly worded rows may be ambiguous. Broad cleanup
could reject the wrong record or rewrite valid history.

## Target Behavior

Harness previews conservative legacy reconciliation, applies only unambiguous
metadata backfills after an explicit action, and leaves ambiguous/manual records
unchanged for human selection. Historical evidence and terminal outcomes are
never deleted or rewritten.

## Affected Users

- Maintainers upgrading existing Harness databases.
- Humans reviewing legacy proposals and duplicates.
- Agents validating fresh rebuild and installer migration.

## Affected Product Docs

- `docs/stories/epics/E09-self-improving-harness-lifecycle/README.md`
- `docs/decisions/0008-self-improving-harness-lifecycle.md`
- `docs/IMPROVEMENT_PROTOCOL.md`
- `docs/HARNESS_BACKLOG.md`

## Dependencies

- Blocked by: `US-075`, `US-078`.
- Blocks: none.

## Acceptance Criteria

- A deterministic report classifies each legacy row as derivable, manual,
  ambiguous, or duplicate candidate and explains why.
- Dry-run shows exact proposed metadata changes and leaves database and changeset
  hashes unchanged.
- Apply backfills only nullable stable identity/evidence metadata for uniquely
  derivable rows.
- UID-less legacy trace/intervention evidence is never assigned invented row
  identity. Apply captures an immutable replay-safe `legacy_snapshot` containing
  the exact canonical evidence used and links that snapshot to the reconciled
  backlog occurrence.
- Repeating apply reuses a snapshot with the same source kind and full
  fingerprint; replay never looks up the diagnostic source-local id.
- Live-equivalent backlog #6/#7 rows become tracked/pending under stable keys
  without automatic acceptance, rejection, implementation, or duplication.
- Manual and ambiguous rows remain unchanged.
- Duplicate candidates are reported; no automatic canonical choice or rejection
  occurs.
- Terminal status, outcome, closure time, and raw evidence are never rewritten.
- A keyed terminal row with nonblank legacy `actual_outcome` receives one neutral
  append-only `legacy_recorded` outcome observation. The original field remains
  unchanged and Harness does not infer confirmed/ineffective/reverted semantics.
- Changed apply is one transaction, one replayable operation set, and one
  operational trace; dry-run/no-op records no mutation trace.
- Live migration, fresh rebuild, and local installer upgrade produce the same
  classification and metadata.

## Non-Goals

- Do not automatically reject duplicate rows.
- Do not automatically choose the oldest row as canonical.
- Do not accept pending proposals for the human.
- Do not assign `trc_`/`int_` uids to legacy rows whose original identity and
  timestamp cannot be recovered.
- Do not delete or merge traces, interventions, friction, stories, or backlog
  history.

## Implementation Evidence

- Added schema migration `011-legacy-evidence-snapshots.sql` with immutable,
  fingerprint-deduplicated embedded evidence.
- Added explicit dry-run/apply reconciliation with conservative classification
  and derivable-only mutation.
- Added replay support that uses embedded evidence instead of replay-local
  trace/intervention ids.
- Added focused live-equivalent #6/#7, terminal-outcome, no-op, and offset-id
  replay coverage under `legacy_proposal_reconciliation`.
