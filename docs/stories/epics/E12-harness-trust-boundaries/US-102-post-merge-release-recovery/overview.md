# Overview

## Current Behavior

Post-merge run `29222332569` prepared and tagged Harness CLI `0.1.16`, then
failed all five build jobs after the candidate binaries had already built and
passed their own smoke tests. The release transition reused the current
protocol smoke for the old `0.1.14` upgrade-source binary. That old binary
allows a mutating SQL CTE, while the current smoke correctly requires the
candidate to reject it.

Pull-request validation tests only the current debug binary and does not execute
the published-old-to-current transition. Maintenance also creates the tag
before release proof, so the failure left `harness-cli-v0.1.16` without a
GitHub Release or assets.

## Target Behavior

- `0.1.14` runs a frozen, version-specific upgrade-source baseline.
- The built candidate and the installed candidate run the current strict smoke.
- Pull requests execute an old-to-candidate transition on Linux and Windows.
- Post-merge maintenance prepares a versioned commit without tagging it.
- The publish job creates the annotated tag only after all platform jobs pass.
- Existing tags must resolve to the exact candidate commit and are never moved.
- The correction produces a later patch release; it does not rewrite `0.1.16`.

## Affected Users

- Harness maintainers publishing CLI releases.
- Installed Harness consumers upgrading from the initial protocol release.
- Agents relying on the pinned release marker during bootstrap.

## Affected Product Docs

- `docs/decisions/0010-proof-before-cli-release-promotion.md`
- `docs/decisions/0005-prebuilt-rust-harness-cli.md`
- `scripts/README.md`
- `docs/stories/epics/E12-harness-trust-boundaries/README.md`

## Non-Goals

- Move or delete `harness-cli-v0.1.16`.
- Weaken current SQL, completion, installer, checksum, or platform proof.
- Change the Harness CLI protocol or database schema.
- Reintroduce Symphony source or state into the Harness release.
