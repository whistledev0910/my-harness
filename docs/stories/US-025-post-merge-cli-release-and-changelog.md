# US-025 Post-Merge CLI Release And Changelog

## Status

implemented

## Lane

normal

## Product Contract

Merged pull requests should leave a project-visible changelog entry. If a
merged PR changes the Rust Harness CLI tool or its release packaging, the repo
should publish a fresh CLI release for downstream installers.

## Relevant Product Docs

- `README.md`
- `scripts/README.md`
- `docs/decisions/0005-prebuilt-rust-harness-cli.md`
- `CHANGELOG.md`

## Acceptance Criteria

- Merged PRs to `main` prepend a summary entry to `CHANGELOG.md`.
- PRs that do not touch CLI files update only the changelog.
- PRs that touch CLI source, schema, Cargo metadata, or release packaging bump
  the CLI patch version, update `scripts/harness-cli-release-tag`, prove the
  exact candidate on every platform, create a matching annotated
  `harness-cli-v*` tag, and publish release assets.
- Automatic and manually dispatched releases use the same prove-then-promote
  workflow. A direct tag push is not a publication entry point.
- Historical upgrade sources run a frozen version-specific contract; current
  candidate binaries run the current strict contract.
- Failed release tags remain immutable and recovery advances to a later patch
  version.

## Design Notes

- Commands: GitHub Actions workflows.
- Domain rules: CLI release detection is path-based and scoped to files that can
  affect the Rust CLI binary, schema, Cargo metadata, or packaging output.
- Release flow: the post-merge workflow commits maintenance metadata and calls
  the reusable workflow with that exact commit. The release workflow verifies
  and builds it, then the publish job creates the tag with a non-force push.

## Validation

When updating durable proof status, use numeric booleans:
`scripts/bin/harness-cli story update --id US-025 --unit 1 --integration 1 --e2e 0 --platform 0`.

| Layer | Expected proof |
| --- | --- |
| Unit | YAML and shell syntax checks pass for changed workflows. |
| Integration | Existing Rust workspace tests still pass. |
| E2E | Not run locally; GitHub merge event required. |
| Platform | Release workflow still targets macOS arm64, macOS x64, Linux x64, Linux arm64, and Windows x64. |
| Release | Manual/reusable candidates are proven before an immutable tag and assets are created. |

## Harness Delta

The Harness release process now includes automatic changelog recording and
conditional CLI release preparation after merged pull requests.

## Evidence

- `ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f); puts "ok #{f}" }' .github/workflows/harness-cli-release.yml .github/workflows/post-merge-maintenance.yml`: passed.
- `cargo test --workspace`: passed, 20 tests.
- `cargo fmt --check`: passed.
- `cargo clippy --workspace -- -D warnings`: passed.
- `bash -n scripts/install-harness.sh && bash -n scripts/build-harness-cli-release.sh`: passed.
- `actionlint`: not installed locally, so GitHub-specific workflow linting was not run.
- 2026-06-09 follow-up: GitHub run `27180707313` failed in
  `Update maintenance files` because changelog bullet `printf` formats began
  with `-` and were parsed as options on the runner. The workflow now uses
  `printf --` for all bullet formats. Local reproduction of the PR #13
  changelog entry passed.
- 2026-07-13 follow-up: run `29222332569` proved that applying the evolving
  current smoke to the immutable `v0.1.14` upgrade source is invalid and that
  tag-first sequencing can strand a release identity. `US-102` and decision
  `0010` separate the historical/current contracts and move tag creation behind
  the complete platform matrix.
