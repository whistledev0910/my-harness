# Design

## Domain Model

An `epoch` identifies one active replay set. The legacy source epoch remains
immutable archive evidence. Core starts a fresh active epoch; Symphony
continues the product-owned epoch initialized by `US-093`.

An exported row has:

- stable UID/local legacy ID;
- record kind;
- source epoch;
- owner product;
- target action;
- reason/evidence checksum.

## Application Flow

```text
backup DB + raw log + hashes
  -> add synthetic generic fixtures
  -> prove generic replay
  -> export live ownership slices
  -> discover every user table and prove FK/disposition closure
  -> prepare fresh core DB in a temp path
  -> stage reviewed target additions through the target CLI
  -> compare counts/identities/invariants
  -> journal and activate the core DB + log-directory epoch pair under fence
  -> run all decisive audits/replay against the switched pair while fenced
  -> mark transition complete and release writers only after green proof
```

## Interface Contract

The validation script accepts an explicit fixture directory and reports generic
operation/invariant counts. It does not inspect project story IDs.

The partition report includes every discovered user table and exact disposition
for backlog `#9`-`#14`, UI tool providers, `US-032`-`US-071`, `US-SYM-001`,
core E09/E10, and E11. It fails when a table or row lacks a disposition, a
retained/moved foreign key points to a discarded row, or per-table stable-UID
sets differ after migration.

## Data Model

Mixed legacy files:

- seed: core `US-028`-`US-031`; Symphony `US-032` onward in that file;
- US-065: Symphony story evidence plus core backlog `#13`;
- US-072: core audit/provider story plus Symphony verification/providers.

Original files are never edited. Fresh projections, if needed for evidence,
use new headers/run IDs and are never applied incrementally to a DB that already
applied the originals. Target additions are newly recorded CLI operations, not
legacy projections replayed over the `US-093` database.

At partition time, a second cutoff manifest extends the frozen 32-file baseline
with every later E11 semantic file. `changeset_applied` is epoch-derived: the
new core DB records only content-hash-validated operations intentionally applied
to that epoch. `schema_version` comes from normal migrations. Tool/provider
presence is recomputed from retained core records, not copied cache state.

The new core epoch preserves every E11 row needed for the final source graph and
foreign-key closure: `US-090`/`US-091` remain completed migration evidence, and
target work packets `US-093`-`US-096` appear only as completed or `changed`
receipt proxies. All original source edges remain. These rows are coordination
evidence, never runnable product backlog. This allows `US-097`
preparation/activation to run in parallel with target `US-096` without deleting
the proxy that gates `US-098` and `US-100`.

## UI / Platform Impact

No product UI change. Default selection/backlog/provider queries stop offering
the other product's work because the active DB is ownership-correct. Matrix may
show only explicit completed/`changed` E11 receipt proxies as coordination
history; none is runnable product backlog.

## Observability

Before/after reports include schema versions, table counts, stable identities,
per-table UID sets, foreign-key closure, open/runnable work, registered tools,
audit/proposal output, cutoff manifests, and checksums.

## Alternatives Considered

1. Delete Symphony rows in place. Rejected because it rewrites local evidence
   without a reproducible ownership export.
2. Keep all old logs active and merely retire stories. Rejected for this
   template because it retains the noisy product replay set and does not fix
   the incomplete 84-versus-59 reconstruction.
3. Move whole changeset files by filename. Rejected because three files contain
   operations owned by both products.
