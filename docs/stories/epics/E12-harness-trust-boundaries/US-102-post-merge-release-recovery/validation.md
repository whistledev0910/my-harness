# Validation

## Proof Strategy

Reproduce the historical mismatch as a positive compatibility boundary: the
old binary passes only its frozen protocol-discovery baseline, while both the
raw and installed candidates pass the full current smoke. Static workflow and
identity negatives prove that tags cannot precede the matrix or drift from the
candidate commit.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Release path classification and strict/candidate identity argument handling. |
| Integration | `0.1.14` frozen baseline, old-to-candidate installer transition, candidate full smoke. |
| E2E | Post-merge candidate commit flows through verify/build before tag creation and publication. |
| Platform | Linux and Windows transition before merge; five-platform release matrix after merge. |
| Performance | No material expansion of the shared Rust validation path. |
| Logs/Audit | Failures name version/commit/tag mismatches; workflow contract proves publication ordering. |

## Fixtures

- Published and checksum-verified `harness-cli-v0.1.14` platform artifacts.
- Current debug/release candidate binaries.
- Temporary Git repositories with absent, matching, mismatched, and wrong-version tags.
- Workflow text fixtures checked for dependency and tag-creation placement.

## Commands

```text
tests/release/test-post-merge-release-recovery.sh
scripts/validate-premerge.sh
```

Hosted proof additionally runs the Linux and Windows old-to-candidate
transitions in the pull-request workflow.

## Acceptance Evidence

- Failed hosted run `29222332569` was reproduced locally. The candidate build,
  checksum, installer upgrade, consumer-file preservation, and candidate smoke
  passed; the old `v0.1.14` binary then exited `0` for the mutating SQL CTE that
  the current smoke requires to exit `1`.
- `tests/release/test-post-merge-release-recovery.sh` passes identity negatives,
  first-writer and same-run promotion behavior, immutable collision rejection,
  five-platform workflow routing, and release-affecting path classification.
- A pinned macOS arm64 `v0.1.14` artifact with SHA-256
  `0adcd5360cd636c189fe0cd958e5b73261f7012a4e43631f08c61269c785caf9`
  passed the frozen smoke, upgraded to the current `0.1.16` candidate, and the
  installed candidate passed the current strict smoke.
- `scripts/validate-premerge.sh` passed all 90 Rust tests, format, clippy,
  revision/bootstrap/ownership negatives, protocol and installer tests,
  documentation/effect checks, and release recovery contracts.
- Checksum-verified `actionlint v1.7.12` accepted all GitHub Actions workflows.
- The default local database still contains the pre-cutover Symphony epoch, so
  bootstrap correctly refused it. Intake `#1`, decision `0010`, and `US-102`
  were recorded in an isolated task database and replayable semantic changeset;
  the mixed database was not modified.
- Pull-request run `29223964557` passed on the first attempt. Ubuntu completed
  the full repository contract and pinned Linux x64 transition; Windows
  completed the pinned download, frozen smoke, installer upgrade, and current
  installed-candidate smoke.
- `story verify US-102` reran the release recovery contract successfully. Trace
  `#1` is detailed `3/3`, and intervention `#1` records the human correction
  that reopened the prematurely completed release outcome.
- The eventual five-platform `v0.1.17` promotion remains merge-gated, so the
  story stays `in_progress` with E2E/platform proof unset.
