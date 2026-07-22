# Design

## Domain Model

A release candidate is the tuple:

```text
requested semantic version
+ exact candidate commit
+ crate version
+ five platform artifacts and checksums
```

A release tag is promotion evidence for that proven tuple, not an input that
must exist before the build begins.

Historical and current protocol expectations are separate:

```text
old upgrade source -> frozen old-version baseline
candidate artifact -> current full protocol smoke
installed candidate -> current full protocol smoke
```

## Application Flow

1. Maintenance classifies release-affecting paths and writes the next patch
   version into a candidate commit.
2. It calls the reusable workflow with the candidate commit and requested tag,
   but does not create the tag.
3. Candidate identity verifies tag syntax, crate version, and commit ownership.
   Only this path may proceed while the tag is absent.
4. Every platform builds, checksums, smokes the candidate, verifies the frozen
   `0.1.14` baseline, upgrades it, and smokes the installed candidate.
5. After the complete matrix passes, publication checks out the same commit,
   creates the annotated tag if absent, verifies strict tag identity, and
   publishes the collected artifacts.

## Interface Contract

- Normal release identity remains strict: the tag must exist, resolve to
  `HEAD`, and match the crate version.
- An explicit `--allow-unpublished` verification mode permits an absent tag but
  still rejects an existing tag at another commit.
- The reusable workflow exposes that mode only to its post-merge caller.
- `harness-cli-v0.1.14` remains the named compatibility floor until a separate
  decision changes it.

## Data Model

No SQLite or protocol schema changes are required. Release identity is stored
in Git commits, annotated tags, workflow inputs, checksums, and GitHub Release
assets.

## UI / Platform Impact

Bash and PowerShell receive equivalent frozen-baseline checks. The full release
matrix remains macOS arm64/x64, Linux arm64/x64, and Windows x64. Pull requests
exercise one Linux and one Windows transition to catch contract drift before
merge.

## Observability

Compatibility scripts emit the expected historical version and protocol tuple.
Identity failures distinguish missing tags, mismatched commits, and version
mismatches. Workflow contract tests prove that tag creation is located after
the build dependency rather than in maintenance preparation.

## Alternatives Considered

1. Test only `--version` after upgrade. Rejected because current candidate
   behavior must still pass the full protocol smoke.
2. Copy the entire historical smoke and schema. Rejected because the upgrade
   source needs only a stable executability/protocol baseline before replacement.
3. Let `gh release create` choose the tag target implicitly. Rejected because
   the proven candidate commit must be explicit and verified.
