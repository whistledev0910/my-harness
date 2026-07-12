# Design

## Domain Model

The source boundary check classifies references as:

- `active_forbidden`: runtime, current product docs, current work, verification,
  installer, or release coupling;
- `historical_allowed`: ADR, completed E11 evidence, dated changelog/PR/archive;
- `generic_origin_note`: short explanation in a retained capability's history.

Any unclassified Symphony reference fails validation.

## Application Flow

```text
verify target candidate + history partition
  -> cap maintenance changelog noise
  -> remove workspace/source/product-owned paths
  -> generalize retained core history/docs
  -> clean installer/ignore/release surfaces
  -> run boundary and link checks
  -> hand off to full core regression
```

## Interface Contract

No existing Harness CLI command is removed. Root `cargo` commands continue to
work, now selecting the one CLI member. Installed Harness files remain declared
once in `scripts/harness-install-files.txt`.

## Data Model

Schemas and CLI migrations stay intact. Active repository operational logs are
already partitioned by `US-097`. Cleanup does not issue SQL deletes against a
legacy DB.

Receipt proxies remain completed history. Their verification is repointed by a
logged CLI mutation from the temporary root gate script to a self-contained E11
evidence verifier that checks committed receipt/manifest hashes locally. This
keeps `verify-all` green without leaving Symphony migration logic in the core
runtime or installer.

Ignore policy distinguishes the template repository from its consumers:
repository-harness removes its current live files, while the installed generic
rule continues to unignore/allow consumer semantic changesets. A fresh-consumer
fixture proves the distinction instead of deleting the exception merely to
make the source tree empty.

## UI / Platform Impact

Harness has no UI or desktop surface after cleanup. UI-specific ignored paths,
providers, tests, and hooks leave the core.

## Observability

The cleanup report lists removed, retained/generalized, and allowlisted paths,
plus the target commit that owns every moved source.

## Alternatives Considered

1. Leave stubs and local redirects at old paths. Rejected because agents would
   continue treating Symphony as active source work.
2. Remove E04/schema/replay capabilities because they began for Symphony.
   Rejected because they are generic, released Harness behavior.
3. Require zero occurrences of the word Symphony. Rejected because the ADR and
   migration history must explain what changed.
