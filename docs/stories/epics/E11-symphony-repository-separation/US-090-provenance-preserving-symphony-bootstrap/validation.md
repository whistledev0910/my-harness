# Validation

## Proof Strategy

Prove both positive lineage (wanted commits remain) and negative scope (forbidden
Harness source and binary snapshots do not enter the target).

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Manifest-to-filter input has deterministic ordering and no duplicate paths. |
| Integration | Old-to-new map resolves selected representative source commits. |
| E2E | Fresh clone of target contains expected files and raw-import tag. |
| Platform | Git operations use portable paths and do not depend on the original working tree. |
| Performance | Filtered repository size is recorded and excludes historical SQLite blobs. |
| Logs/Audit | Source refs before/after match; target provenance contains all immutable anchors. |
| Remote safety | Dry-run/command capture contains exactly `HEAD:main` and the raw-import tag refspec. |

## Fixtures

- Verified `US-089` bundle.
- Exact path manifest.
- Empty target remote.

## Commands

```bash
git bundle verify <source.bundle>
git filter-repo --version
shasum -a 256 -c <git-filter-repo-checksum-file>
git log --follow -- crates/harness-symphony/src/main.rs
git log --follow -- crates/harness-symphony/web-ui/src/main.tsx
tests/migration/assert-filter-scope.sh --expected-head main --expected-tag "$RAW_IMPORT_TAG"
git fsck --full
git ls-remote --heads --tags origin
```

The scope script fails on any Git/`rg` error, requires exactly the reviewed
head/tag refs, and rejects Harness CLI/database/hidden-tool paths; “no match” is
handled explicitly rather than with `|| true`.

## Acceptance Evidence

Completed 2026-07-12 after the fresh owner go/no-go recorded in the external
owner-only vault:

- Frozen source: `6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9`.
- Filtered/provenance commit and remote `main`:
  `5db694c8fd43a7d0e34bd9eaf9030d18b856f2b5`.
- Annotated tag `symphony-raw-import-20260712` peels to the same commit.
- Exact 100-path manifest SHA-256:
  `e949ed330ace1e6ae80aa0bbe737dce831732d18bef62edf288eb00f8de876cf`.
- Recovery bundle SHA-256:
  `cc6b868567750e139d167e8b674d8016359e0e8c66307446ef15fe6ae4df712d`.
- Source refs before/after are byte-identical. Only `HEAD:main` and the reviewed
  annotated tag were pushed; no mirror/all-ref push occurred.
- Both the disposable filtered repository and a fresh clone pass the
  fail-closed scope verifier and `git fsck --full`.
- `/Users/themrb/Documents/personal/symphony` is materialized at the reviewed
  remote commit with a clean `main` tracking `origin/main`.
- `scripts/test-verify-e11-us090.sh` proves the story wrapper rejects a clean
  Git repository with unrelated history.
