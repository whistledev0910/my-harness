# Validation

## Proof Strategy

Prove identity using multiple changesets whose source databases use different
local integer ids, then rebuild and compare new stable uids, evidence coverage,
and v2 source timestamp bytes. Separately prove v1 rows remain nullable and their
unrecoverable legacy timestamps are excluded from parity.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Unicode-safe full-key/display-label generation, rule-version behavior, uid parsing, occurrence-kind validation, and audit finding fingerprints. |
| Integration | v8-to-v9 null legacy migration; strict intake/backlog/trace/intervention add@v1/v2 dispatch; new uid/time persistence; audit open/no-op/clear/reappear episodes; one-open-key enforcement; observation schema; FK/uniqueness rollback. |
| E2E | Changeset A writes v2 intake, trace, and backlog uids; changeset B writes an intervention referencing the trace uid; deliberately offset local integer ids still rebuild the same intake-trace-intervention graph. |
| Platform | Local release artifact and installer create/migrate the new schema. |
| Performance | Key and uid lookup use indexes; proposal scans remain bounded on the current trace volume. |
| Logs/Audit | Rendered changesets and queries expose uid, proposal key, predecessor, and evidence coverage. |

## Fixtures

- Existing schema-v8 database with manual and generated backlog rows.
- v1 and v2 changesets with intentionally different local integer ids.
- Unicode friction and intervention text.
- Same-second evidence and closure records.
- Multiple closed occurrences sharing one proposal key.
- Unchanged, cleared, reappeared, and canonical-facts-changed audit findings.

## Commands

```bash
cargo fmt --check
sh -c 'cargo test -p harness-cli -- --list | rg "improvement_identity" && cargo test -p harness-cli improvement_identity -- --nocapture'
scripts/validate-changeset-rebuild.sh
cargo clippy --workspace -- -D warnings
git diff --check
```

## Acceptance Evidence

Add exact migration, test, rebuild, and installer outputs after implementation.
