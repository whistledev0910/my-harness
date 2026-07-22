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

Release evidence completed on 2026-07-12:

- Protocol tag `harness-cli-v0.1.14` peels to exact develop commit
  `d2f89eeabe8d01df95fd19cd6ba981b01a71730f`; `main` was not promoted.
- Release run `29177994849` passed Verify, macOS ARM64/x64, Linux ARM64/x64,
  Windows x64 PowerShell protocol/snapshot smoke, and publication.
- The public release contains all five binaries and five checksum files. The
  downloaded files verify to:
  - macOS ARM64: `0adcd5360cd636c189fe0cd958e5b73261f7012a4e43631f08c61269c785caf9`
  - macOS x64: `d0ee0b6b9f702eb87824e96b42d7a8382012b542a076e8ce2d0b1bb8d6201168`
  - Linux ARM64: `8828d624075fbae2f44b6f57ac651bdacb2e7c60ed0cc15853b9481b3edf0161`
  - Linux x64: `d2551d32490d0af78f8eb387d8854771ebfcde2260b068539384592668cc54a6`
  - Windows x64: `abd5a4176d52b3576c66932f44f377d2667fba409011de145044f425fd0a82ca`
- Windows produced a different byte hash between rehearsal and publication;
  both exact binaries passed the native smoke, the published checksum verifies,
  and the owner explicitly accepted the published checksum.
- Immutable tags `harness-cli-v0.1.12` and `harness-cli-v0.1.13` have no GitHub
  releases: their fail-closed jobs respectively exposed the app-server stdout
  race and Windows snapshot-handle bug fixed in v0.1.14.
- The contract records `HARNESS_PROTOCOL_V1_TAG=harness-cli-v0.1.14` for
  downstream US-093 and US-095 compatibility gates.
