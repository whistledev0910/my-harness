# Design

## Domain Model

- Derivable legacy row: provenance and exact rule inputs are sufficient to
  generate one stable proposal key without semantic guessing.
- Ambiguous row: several keys or no key could reasonably match.
- Duplicate candidate: two occurrences share a derivable issue identity but
  canonical status/outcome requires human review.

## Application Flow

1. Scan legacy backlog rows and classify derivable, ambiguous, manual, and
   duplicate-candidate records.
2. Render a deterministic dry-run report with proposed metadata changes and
   reasons for every skip.
3. On explicit apply, backfill only derivable nullable metadata in one
   transaction.
4. Record one operational trace only when rows actually change.
5. Emit semantic operations so fresh rebuild produces the same classification.

## Interface Contract

Use the maintenance-specific commands:

```bash
scripts/bin/harness-cli backlog reconcile \
  --action backfill-lifecycle-identity --dry-run
scripts/bin/harness-cli backlog reconcile \
  --action backfill-lifecycle-identity --apply
```

Analysis and mutation are never hidden behind default `propose`.

## Data Model

Backfill nullable stable backlog identity/evidence metadata introduced by E09.
Migration `011-legacy-evidence-snapshots.sql` adds:

```text
legacy_evidence_snapshot(
  uid,                    -- leg_<32 lowercase hex>
  source_kind,            -- trace | intervention
  source_local_id,        -- diagnostic hint, never replay identity
  evidence_fingerprint,   -- full 64-hex SHA-256 of canonical_payload
  canonical_payload,      -- immutable canonical JSON embedded in the operation
  captured_at,
  PRIMARY KEY (uid),
  UNIQUE (source_kind, evidence_fingerprint)
)
```

`legacy.evidence.capture@v1` serializes every field, so apply never needs to find
the same replay-local trace/intervention integer id. Reconciled occurrences link
these rows through `proposal_evidence_link.source_kind=legacy_snapshot`. If the
exact supporting payload cannot be selected deterministically, the backlog row
remains ambiguous and unchanged.

For a terminal row with nonblank legacy `actual_outcome`, apply also appends
ordinal 1 in `backlog_outcome_observation` with status `legacy_recorded`, the
unchanged legacy text as `outcome`, and evidence `migrated from
backlog.actual_outcome`. This is preservation, not a measured classification.
Terminal status, actual outcome, implemented/rejected time, and raw evidence are
immutable. Ambiguous rows remain nullable and queryable.

## UI / Platform Impact

CLI only. Installer/migration proof must cover an existing v8 database and a
fresh install.

## Observability

Dry-run writes nothing. Apply shows each backlog key, embedded legacy snapshot,
and neutral migrated outcome before writing. It emits one detailed summary and
one operational trace if rows changed; no-op apply emits no mutation trace.

## Alternatives Considered

1. Keep the oldest row automatically. Rejected because a newer row may be the
   accepted or better-evidenced occurrence.
2. Match similar wording with an LLM. Rejected because migration must be
   deterministic and auditable.
3. Delete duplicates. Rejected because closed and rejected history remains
   useful evidence.
