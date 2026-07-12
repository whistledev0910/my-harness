# Validation

## Proof Strategy

Prove generic operation semantics independently, then compare ownership-aware
fresh databases before atomic activation.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Dynamic table inventory, fixture operation versions, mixed-operation classifier, new run-ID enforcement, FK closure. |
| Integration | Synthetic changeset apply/rebuild, idempotence, crash-injected journal recovery, fresh core DB preparation, epoch-derived state, target CLI reconciliation. |
| E2E | Core and Symphony queries show only product-owned runnable work; a surviving `changed` US-096 proxy blocks source cleanup until receipt. |
| Platform | Backup/replace works with WAL reconciliation and platform path differences. |
| Performance | Record archive/rebuild duration and sizes; no requirement to replay product history in core CI. |
| Logs/Audit | Checksums, row dispositions, audit/proposal output, zero wrong-owner runnable/backlog/provider records, and only allowlisted E11 receipt proxies visible. |

## Fixtures

- Immutable archive of the 32-file frozen baseline plus a separately hashed,
  manifest-derived partition cutoff containing every post-baseline E11 file.
- Synthetic generic replay set.
- Live source DB backup.
- Temporary fresh core database and backup of the existing target database.

## Commands

```bash
shasum -a 256 -c <archive-checksums>
cargo test -p harness-cli --locked
scripts/validate-changeset-rebuild.sh
scripts/test-validate-changeset-rebuild.sh
scripts/verify-e11-inventory.sh --require-zero-unknown --require-fk-closure --compare-uid-sets
HARNESS_DB_PATH=<fresh-core> scripts/bin/harness-cli audit
HARNESS_DB_PATH=<fresh-core> scripts/bin/harness-cli query matrix
HARNESS_DB_PATH=<fresh-core> scripts/bin/harness-cli query backlog
HARNESS_DB_PATH=<fresh-core> scripts/bin/harness-cli query tools --summary
tests/history/assert-no-live-root-changesets.sh
tests/installer/assert-consumer-changeset-trackable.sh
git diff --check
```

The history assertion fails on Git/tool errors and passes only when no live
root path remains; the consumer fixture separately proves the generic tracking
rule still works.

## Acceptance Evidence

Pending implementation. Attach backup verification, fixture coverage mapping,
all-table row-disposition/FK export, per-table count/UID comparison, epoch-state
report, crash-recovered DB/log pair proof, preserved E11 proxy/edge proof,
fresh-consumer tracking proof, and rollback rehearsal.
