# Exec Plan

## Goal

Bring safely derivable legacy improvement rows into the E09 lifecycle without
rewriting ambiguous or historical evidence.

## Dependencies

- Blocked by: `US-075`, `US-078`.
- Consumes: selective acceptance identity and final recurrence classification.
- Produces: conservatively reconciled legacy state and migration proof.
- Ready when: both prerequisite stories are implemented and dependency edges are
  complete.

## Scope

In scope:

- Read-only legacy classification report.
- Explicit dry-run and guarded metadata backfill.
- Additive `011-legacy-evidence-snapshots.sql`, immutable embedded snapshots, and
  `legacy.evidence.capture@v1` replay.
- Neutral `legacy_recorded` observations for nonblank legacy actual outcomes.
- Live-equivalent #6/#7 fixtures.
- Transactional mutation, trace behavior, and changeset replay.
- Installer upgrade fixture.

Out of scope:

- Automatic duplicate rejection or canonical choice.
- Semantic/LLM matching.
- Historical evidence deletion.
- Automatic proposal acceptance.

## Risk Classification

Risk flags:

- Data model.
- Existing behavior.
- Weak proof.

Hard gates:

- Migration of existing durable records.
- Protection of closed/rejected history.

## Work Phases

1. Build a v8 legacy fixture from representative generated and manual rows.
2. Implement deterministic classification and dry-run rendering.
3. Add migration 011 and embedded legacy-evidence snapshot operations.
4. Add guarded derivable-only key/link backfill and neutral outcome preservation.
5. Add operational trace and semantic operation behavior.
6. Prove no-op and ambiguous-row immutability.
7. Validate live migration, fresh rebuild, and local installer upgrade.

## Stop Conditions

Pause for human confirmation if:

- A row needs semantic guessing to select a proposal key.
- A terminal status or actual outcome would need mutation.
- More than one plausible canonical duplicate exists.
- Fresh rebuild does not reproduce the live reconciliation result.
