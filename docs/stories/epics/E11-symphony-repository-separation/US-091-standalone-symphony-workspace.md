# US-091 Standalone Symphony Workspace

## Status

planned

## Owner Repository

`symphony`

## Lane

normal with existing-behavior and cross-platform proof.

## Product Contract

The filtered target becomes a normal one-product Rust workspace without
flattening the imported crate. It builds from a clean clone and has no Cargo
source dependency on repository-harness.

## Relevant Product Docs

- Target provenance note from `US-090`.
- Target Symphony scope and Quickstart.

## Acceptance Criteria

- Root `Cargo.toml` has exactly one member: `crates/harness-symphony`.
- Root `[workspace.package]` explicitly defines the inherited `edition`,
  `license`, and `repository`; repository metadata points to
  `https://github.com/hoangnb24/symphony`.
- `Cargo.lock` is regenerated and contains `harness-symphony` but no
  `harness-cli` package.
- Root README, LICENSE, `.gitignore`, Rust version, and Node version make a
  clean contributor checkout reproducible.
- Existing relative npm, Playwright, Electron, and Rust Web asset paths work in
  the preserved layout.
- The source gate passes: 99 Rust tests, Web UI build, 19 Playwright tests,
  desktop smoke, formatting, and all-target clippy.
- CI runs those checks directly, installs Chromium with Playwright system
  dependencies (`playwright install --with-deps chromium`), and no longer
  relies on Harness CLI release CI.
- No manifest or script names a sibling `/repository-harness` checkout.
- Harness template files may be installed in the target after the standalone
  source gate passes, but target durable-state initialization and planning-row
  ownership transfer are deferred to high-risk `US-093`. If a CLI is installed
  here, it is explicitly provisional: `US-093` must use the checksum-verified
  forced upgrade to the exact `US-092` tag before any target DB mutation.
- Source repository-harness code, tracked files, and durable planning rows
  remain unchanged in this story.

## Design Notes

- Workspace: preserve `crates/harness-symphony` for the first release.
- Lockfile: regenerate from target manifests.
- CI: use `npm ci`, not an existing local `node_modules` tree.
- Later flattening must be a separate story after standalone parity.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | Existing 99 Rust tests pass. |
| Integration | Cargo metadata reports one package/member and no path dependency. |
| E2E | Existing 19 Playwright tests pass from a clean clone. |
| Platform | Electron desktop smoke and Windows/macOS/Linux CI path checks pass. |
| Release | Locked release build succeeds. |

```bash
cargo metadata --locked --no-deps --format-version 1
jq -e '.workspace_members | length == 1 and (.packages | length == 1) and (.packages[0].name == "harness-symphony")' < <(cargo metadata --locked --no-deps --format-version 1)
jq -e '.packages | all(.name != "harness-cli")' < <(cargo metadata --locked --format-version 1)
cargo fmt --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --locked
npm --prefix crates/harness-symphony/web-ui ci
npm --prefix crates/harness-symphony/web-ui exec -- playwright install --with-deps chromium
npm --prefix crates/harness-symphony/web-ui run build
npm --prefix crates/harness-symphony/web-ui run e2e
npm --prefix crates/harness-symphony/web-ui run desktop:smoke
git diff --check
```

## Harness Delta

Install the normal Harness template files into the target with merge semantics
after the workspace is stable. Do not copy or initialize source repository
operational state; `US-093` owns the durable boundary.

## Evidence

Completed on target branch `feature/e11-standalone-workspace` at commit
`61e92c2a73ba3381e0d50b11509ba0eeed079bc9`:

- Root Cargo metadata reports exactly one workspace member/package,
  `harness-symphony`, with MIT/edition 2021 and the Symphony repository URL.
- The regenerated `Cargo.lock` contains `harness-symphony` and no
  `harness-cli`; all Cargo dependencies are registry dependencies.
- Rust `1.92.0` and Node `24.9.0` are pinned; README, LICENSE, `.gitignore`, and
  direct Linux/macOS/Windows CI are committed.
- The Web manifest and Electron app id are Symphony-owned. Preserved relative
  asset paths pass build, Playwright, and desktop smoke without `harness.db`.
- The generic Harness template was installed with merge semantics. Its
  downloaded v0.1.11 CLI is ignored/provisional, and no target DB was created;
  US-093 must force-upgrade it to the exact US-092 protocol tag first.
- Local and third-directory fresh-clone gates passed: 99 Rust tests, fmt,
  all-target clippy, locked release build, `npm ci`, Web build, 19 Chromium
  Playwright tests, and Electron desktop smoke.
- `tests/standalone/test-verify-workspace.sh` rejects a two-member fixture that
  contains `harness-cli`; source `scripts/test-verify-e11-us091.sh` rejects
  repository-harness itself as a substitute target.
