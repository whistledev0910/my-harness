# Validation

## Proof Strategy

Use an immutable legacy-v8 fixture containing generated, manual, implemented,
rejected, and ambiguous rows. Compare before/after row snapshots for dry-run,
apply, no-op apply, and fresh rebuild.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Derivable/manual/ambiguous/duplicate-candidate classification and deterministic report ordering. |
| Integration | Dry-run hash unchanged; apply changes only nullable metadata; UID-less evidence becomes embedded immutable snapshots; legacy actual outcome becomes neutral observation; no-op trace behavior; transaction rollback. |
| E2E | Backlog #6/#7 equivalents become tracked under stable keys with complete snapshot coverage, without automatic acceptance or deletion. |
| Platform | Existing database upgrade, deliberately offset replay-local trace ids, semantic changeset replay, and fresh installer migration produce the same snapshot/outcome result. |
| Performance | One bounded legacy scan with indexed stable-key lookup. |
| Logs/Audit | One mutation trace on changed apply; no trace on dry-run/no-op; skipped rows include reasons. |

## Fixtures

- Generated proposed rows equivalent to live backlog #6/#7.
- Manual row with similar wording.
- Implemented and rejected rows with outcomes.
- UID-less legacy traces/interventions whose rebuilt local ids differ.
- Two ambiguous duplicate candidates with different status/evidence quality.

## Commands

```bash
cargo fmt --check
sh -c 'cargo test -p harness-cli -- --list | rg "legacy_proposal_reconciliation" && cargo test -p harness-cli legacy_proposal_reconciliation -- --nocapture'
scripts/validate-changeset-rebuild.sh
cargo clippy --workspace -- -D warnings
git diff --check
```

## Acceptance Evidence

- Focused reconciliation coverage proves dry-run leaves identity untouched;
  apply reconciles two live-equivalent generated rows, captures four UID-less
  evidence snapshots, preserves terminal fields, appends one neutral legacy
  observation, and writes one operational trace.
- Repeated apply reports zero changes and writes no second trace.
- Changeset replay against deliberately offset local trace/intervention/backlog
  ids produces the same two keyed rows, four snapshots, and one observation.
- `scripts/validate-changeset-rebuild.sh` and the workspace validation ladder
  provide repository-wide migration/replay proof.
