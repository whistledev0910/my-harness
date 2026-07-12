# Validation

## Proof Strategy

Test protocol behavior through the compiled CLI at process boundaries, not only
repository methods.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Typed JSON/error schemas, capability comparison, hierarchy cycle detection, CAS conflicts, header/hash validation. |
| Integration | Every listed CLI JSON read/write success/error against missing/current/needs-migration/unsupported DBs; semantic replay, snapshot, and atomic-failure parity. |
| E2E | A black-box fixture performs one-call graph discovery, WAL-safe snapshot, CAS status update, hierarchy query, and changeset apply without SQL. |
| Platform | macOS/Linux binary and Windows `.exe` emit equivalent bounded JSON; Bash/PowerShell forced upgrade verifies the same release tuple. |
| Performance | One JSON read handles the full current story graph without per-story subprocess calls. |
| Logs/Audit | Read-only queries write nothing; mutations produce one expected semantic operation. |
| Release | Immutable tag is newer than v0.1.11; every supported artifact checksum verifies after download. |

## Fixtures

- Fresh schema v12 database.
- Older supported database requiring migration.
- Cyclic and acyclic dependency/hierarchy graphs.
- Applied and unapplied changesets.
- Same run ID with same and changed content; unsupported header/base schema.
- Uncheckpointed WAL commit plus held reader during `db snapshot`.
- Non-UTF-8/space-containing platform paths and oversized/timeout fake output.

## Commands

```bash
cargo fmt --check
cargo test -p harness-cli --locked
cargo clippy -p harness-cli --all-targets -- -D warnings
scripts/validate-changeset-rebuild.sh
scripts/test-validate-changeset-rebuild.sh
scripts/test-install-harness-cli-upgrade.sh
scripts/build-harness-cli-release.sh
gh release view "$HARNESS_PROTOCOL_V1_TAG"
shasum -a 256 -c dist/*.sha256
tests/protocol/smoke-native-artifact.sh dist/<platform-artifact>
powershell -File tests/protocol/smoke-native-artifact.ps1 -Artifact dist/<windows-artifact>
git diff --check
```

## Acceptance Evidence

Pre-release implementation evidence collected on macOS on 2026-07-12:

- `cargo test -p harness-cli --locked`: 77 passed, including non-mutating
  discovery, WAL snapshot, hierarchy/CAS, and changeset-content identity tests.
- `cargo clippy -p harness-cli --all-targets --locked -- -D warnings`: passed.
- `tests/protocol/smoke-native-artifact.sh target/debug/harness-cli`: passed at
  the process boundary. The fixture proves missing-DB discovery creates no DB,
  one-call graph/runnable state, CAS before/after state, cycle `CONFLICT`/exit
  3, changeset status/apply/hash identity, and an integrity-checked snapshot at
  a path containing spaces.
- `scripts/test-verify-e11-us092.sh`: passed. A fake executable that exits zero
  while emitting `{}` is rejected, proving the story verifier fails closed.
- `scripts/test-install-harness-cli-upgrade.sh`: passed for merge skip,
  immutable-ref verified replacement, checksum-failure preservation, mutable
  ref rejection, and ref-without-upgrade rejection. It also asserts that the
  release workflow runs the full Bash smoke on macOS/Linux and the equivalent
  PowerShell smoke on Windows before the publish job can start.
- `git diff --check`: passed.

The repository-wide rebuild validator currently reports the already-completed
US-089 as unverified after semantic replay (entropy 5). This pre-existing replay
baseline is recorded rather than treated as US-092 protocol evidence.

Release evidence remains pending the mandatory owner go/no-go: immutable tag,
published macOS/Linux/Windows artifacts and checksums, native artifact matrix,
PowerShell smoke, and replacement of `PENDING-US-092-RELEASE` in the contract.
