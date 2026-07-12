# Validation

## Proof Strategy

Validate released artifacts and clean installs, then prove the absence of
wrong-owner active context in both repositories.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Release metadata/protocol tuple and checksum parsers. |
| Integration | Initial protocol-tag and cleaned-core Harness installs plus the same released Symphony artifact. |
| E2E | For each named tag: doctor -> work -> prepare -> deterministic execute -> Web -> sync. |
| Platform | Published native CLI artifacts and desktop smoke limitations. |
| Performance | Record startup/run smoke times for regression reference. |
| Logs/Audit | Remote refs, versions, active durable state, worktree disposition, observation window. |

## Fixtures

- Published/retrievable Symphony artifacts.
- Cleaned Harness release/install artifacts.
- Initial `US-092` Harness protocol release/install artifacts.
- Fresh temporary Git repository with one deterministic story.
- Source/target recovery tags, bundles, and DB backups.

## Commands

```bash
shasum -a 256 -c <symphony-checksums>
shasum -a 256 -c <harness-checksums>
<install-clean-harness-fixture>
<unpack-released-symphony>
tests/compatibility/released-cross-repo-smoke.sh --harness-tag "$HARNESS_PROTOCOL_V1_TAG"
tests/compatibility/upgrade-harness-fixture.sh --from "$HARNESS_PROTOCOL_V1_TAG" --to "$HARNESS_CLEAN_CORE_TAG" --verify-checksum
tests/compatibility/released-cross-repo-smoke.sh --harness-tag "$HARNESS_CLEAN_CORE_TAG"
scripts/bin/harness-cli audit
scripts/bin/harness-cli query matrix
scripts/bin/harness-cli query backlog --open
scripts/bin/harness-cli query tools --summary
scripts/bin/harness-cli propose
git worktree list --porcelain
test ! -e .agents && test ! -e .codex && test ! -e .impeccable
git bundle verify <source.bundle>
git diff --check
```

## Acceptance Evidence

Pending implementation. The final report must name the Symphony release and
both Harness release SHAs/tags, artifact checksums, discovered protocol tuples,
both smoke outputs, active-state audit, rollback artifacts, and
observation-window end condition.
