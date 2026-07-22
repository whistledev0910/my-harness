# Exec Plan

## Goal

Create the replay-safe identity foundation required by every later E09 lifecycle
story.

## Dependencies

- Blocked by: `US-073`.
- Consumes: replayable story dependency authoring.
- Produces: stable identity and evidence primitives for `US-075` and `US-076`.
- Ready when: `US-073` is implemented and the durable dependency edge is active.

## Scope

In scope:

- Additive schema migrations for stable occurrence and evidence identity.
- One-open-occurrence enforcement, outcome-review plan fields, and append-only
  outcome-observation storage used by later stories.
- Versioned proposal-key generation as a domain rule.
- Stable intake/backlog/trace/intervention uid, cross-record reference, and
  original-time serialization in semantic changesets.
- Explicit audit-evidence episode recording with no-op/clear/reappearance rules.
- Cross-changeset apply and fresh-rebuild support.
- Detailed/JSON query visibility.
- Installer propagation and migration fixtures.

Out of scope:

- Proposal acceptance and suppression behavior.
- Story-backlog link commands.
- Completion and automatic closure.
- Legacy key mutation beyond safe schema defaults.

## Risk Classification

Risk flags:

- Data model.
- Existing behavior.
- Public contracts.
- Weak proof.

Hard gates:

- Durable data migration.
- Cross-changeset identity semantics.
- Historical timestamp and evidence preservation.

## Work Phases

1. Add failing migration and replay fixtures with shuffled local ids.
2. Define typed proposal, occurrence, and evidence identities.
3. Add schema migration and backfill-safe defaults.
4. Add v2 write operations and strict versioned changeset dispatch.
5. Add explicit audit-evidence reconciliation and semantic operations.
6. Update changeset apply/rebuild to resolve by stable uid.
7. Add query visibility and docs.
8. Validate local migration, fresh rebuild, and installer propagation.

## Stop Conditions

Pause for human confirmation if:

- Stable identity requires deleting or merging existing records.
- Existing changesets cannot be migrated without changing their historical
  meaning.
- Proposal matching would broaden beyond deterministic conservative rules.
- Rebuild parity cannot be proven from committed operations.
