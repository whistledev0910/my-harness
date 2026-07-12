# Validation

## Proof Strategy

This story proves structural ownership and documentation integrity. `US-099`
adds the complete behavioral/release regression gate.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Boundary allowlist and installer manifest/link checks. |
| Integration | One-member Cargo metadata, regenerated lock, installer dry-run. |
| E2E | Fresh Harness install contains a coherent core-only README/docs/schema/CLI surface and can track one consumer changeset. |
| Platform | Bash/PowerShell manifest parity and Windows binary path remain. |
| Performance | CLI CI no longer builds npm/Electron or 99 Symphony tests. |
| Logs/Audit | Removed/retained report, local completed-proxy receipt verification, and no active wrong-owner reference. |

## Fixtures

- Target candidate commit/provenance manifest.
- Clean temporary Harness install destinations.
- Historical reference allowlist.

## Commands

```bash
cargo metadata --locked --no-deps --format-version 1
tests/boundary/assert-harness-only-tree.sh
tests/boundary/assert-symphony-history-allowlist.sh
bash -n scripts/install-harness.sh
<installer-manifest-link-check>
tests/installer/assert-consumer-changeset-trackable.sh
scripts/bin/harness-cli story verify-all
test ! -e scripts/verify-e11-external-gate.sh
git diff --check
```

Both boundary scripts distinguish a clean no-match from command/I/O failure and
fail closed. Any additional historical allowlist entry must be encoded
explicitly before activation.

## Acceptance Evidence

Pending implementation. Attach target ownership links, file inventory diff,
boundary results, and fresh installer tree.
