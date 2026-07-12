# Validation

## Proof Strategy

Prove that the source can be reconstructed and every migration input is known
before testing any extraction.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Manifest parser rejects missing, duplicate, or invalid dispositions. |
| Integration | Bundle verifies; tag and bundle HEAD match the frozen SHA; DB backup opens read-only. |
| E2E | All source baseline commands pass at the recorded SHA. |
| Platform | Remote, worktree, and Windows-relevant generated paths are included. |
| Performance | Record bundle/database/runtime sizes so later archival has a bounded expectation. |
| Logs/Audit | Zero unclassified paths/tables/rows, foreign-key closure, and exact changeset ownership counts are reported. |

## Fixtures

- Source checkout at the accepted SHA.
- Empty Symphony target remote.
- Current live `harness.db` and the manifest-derived frozen changeset set (31
  discovery files plus the later E11 transitional planning file at this plan's
  current state).
- Every registered worktree, including staged, unstaged, untracked, binary,
  ignored, and clean cases.
- All registered local worktrees.

## Commands

```bash
git status --short
git rev-parse develop main HEAD
git bundle verify <bundle>
shasum -a 256 -c <bundle>.sha256
sqlite3 harness.db "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
E11_US089_ARTIFACT_DIR=<external-vault> scripts/verify-e11-us089.sh
E11_US089_ARTIFACT_DIR=<external-vault> scripts/test-verify-e11-us089.sh
git worktree list --porcelain
cargo test --workspace
npm --prefix crates/harness-symphony/web-ui run build
npm --prefix crates/harness-symphony/web-ui run e2e
npm --prefix crates/harness-symphony/web-ui run desktop:smoke
cargo fmt --check
cargo clippy --workspace -- -D warnings
scripts/validate-changeset-rebuild.sh
scripts/test-validate-changeset-rebuild.sh
git diff --check
```

## Acceptance Evidence

Implemented under `evidence/`; raw artifacts use external logical vault
`US-089-20260711-v8`.

- 392 frozen tracked paths and 38 planning-transition paths; zero unknown.
- 16 user tables and 660 live rows have exact reviewed identity/payload
  ownership. SQLite FK, disposition closure, and soft-reference checks pass;
  three missing historical snapshots are explicit archived US-097 exceptions.
- 32 changesets contain 32 unique headers and 322 reviewed non-header
  operations. Checksums and live/applied-ledger discrepancies are recorded.
- All 16 registered worktrees have passing restoration evidence, including the
  real 380-addition/3-deletion Symphony diff.
- WAL-only committed data survives the online backup while a bare main-file
  copy misses it. Every discovered ignored SQLite candidate is retained.
- All eight unreachable commits have checksummed external binary patches.
- A fresh bundle clone at the frozen SHA passed 73 Harness CLI and 99 Symphony
  Rust tests, Web build, 19 Playwright tests, desktop smoke, fmt, clippy,
  changeset rebuild, and validator contract tests.
- Negative fixtures prove tampered checksums, missing operations, unknown rows,
  stale baseline SHA, and forged raw-log hashes fail closed.
