# US-078 Proposal Suppression And Recurrence Classification

## Status

implemented

## Lane

normal

## Product Contract

Proposal output distinguishes new work from already pending, accepted, handled,
regressed, and reconsidered evidence. Historical evidence remains explainable,
but only genuinely uncovered evidence after closure returns as a proposal.

## Relevant Product Docs

- `docs/stories/epics/E09-self-improving-harness-lifecycle/README.md`
- `docs/decisions/0008-self-improving-harness-lifecycle.md`
- `docs/IMPROVEMENT_PROTOCOL.md`
- `docs/HARNESS_AUDIT.md`

## Dependencies

- Blocked by: `US-077`.
- Blocks: `US-079`, `US-080`.

## Acceptance Criteria

- The classifier returns deterministic states: `new`, `pending`, `accepted`,
  `suppressed`, `regression`, and `reconsideration`.
- Same key plus proposed occurrence is shown as pending with the existing backlog
  id; it is not presented as unrelated new work.
- Same key plus accepted occurrence is explained as active work and cannot create
  another open occurrence.
- Same key plus implemented occurrence and only covered evidence is suppressed.
- Matching uncovered evidence after implementation becomes a regression
  candidate linked to the immediately prior occurrence.
- Matching uncovered evidence after rejection becomes a reconsideration
  candidate, not a regression.
- Neither regression nor reconsideration automatically creates backlog work.
- Accepting a regression/reconsideration candidate through the `US-075` command
  creates a new `accepted` occurrence with a new backlog uid, the same proposal
  key, `occurrence_kind=regression|reconsideration`, `predecessor_uid` set to the
  immediately prior terminal occurrence, links to the uncovered evidence, and
  exactly one outcome schedule.
- Rejecting that candidate creates the same new occurrence lineage with status
  `rejected`, covered evidence, closure reason/time, and no outcome schedule.
  Repeating either identical decision is a no-op; terminal predecessors are never
  reopened or mutated.
- Similar but non-identical evidence remains separate unless the same explicit,
  versioned rule generates the same key.
- `propose --show-suppressed` explains the occurrence, resolver, closure proof,
  and lack of uncovered evidence.
- Proposal ordering is deterministic by stable key.
- General lifecycle classification replaces issue-specific hard-coded suppression
  when the new model can express the same result.
- Modern keyed fixtures are lifecycle-classified without issue-specific row ids.
  Plausible unkeyed legacy matches remain `legacy-unclassified` and direct the
  operator to `US-080` reconciliation; this story never guesses their identity.

## Design Notes

- Commands: `propose`, `propose --show-suppressed`, selective acceptance from
  `US-075`.
- Queries: compare current stable evidence uids with evidence covered by open and
  closed occurrences.
- API: CLI output plus machine-readable form if required for stable consumers.
- Tables: identity/evidence coverage from `US-074`, relationships/closure from
  `US-076`/`US-077`.
- Audit recurrence consumes the explicit active `audit_evidence_episode` uid; a
  cleared finding that later reappears therefore differs from its covered episode
  even when its canonical facts are identical.
- Domain rules: implemented recurrence is regression; rejected recurrence is
  reconsideration; selective accept/reject persists a new occurrence; old rows
  are not reopened.
- UI surfaces: terminal only.

## Non-Goals

- Do not mutate or backfill unkeyed legacy rows.
- Do not automatically accept regression or reconsideration candidates.
- Do not reopen implemented or rejected occurrences.
- Do not use fuzzy or LLM-based proposal matching.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | State table covers every open/closed/evidence combination and deterministic ordering. |
| Integration | Covered old evidence suppresses; one uncovered evidence uid produces one recurrence; accept/reject persists exact kind/predecessor/coverage/schedule semantics; repeat propose/decision is idempotent. |
| E2E | Accept, complete, rebuild, suppress, add post-closure evidence, then accept or reject one human-gated recurrence into a new lineage occurrence. |
| Platform | Live and rebuilt databases return the same proposal states and predecessor links. |
| Release | Docs, help, workspace fmt/test/clippy, and local installer smoke pass. |

Planned story verification:

```bash
sh -c 'cargo test -p harness-cli -- --list | rg "proposal_recurrence" && cargo test -p harness-cli proposal_recurrence -- --nocapture && scripts/validate-changeset-rebuild.sh'
```

## Harness Delta

Proposal output becomes lifecycle-aware instead of relying on deletion or
one-off suppression rules.

## Evidence

- `cargo test -p harness-cli proposal_recurrence -- --nocapture` covers new,
  pending, accepted, suppressed, regression, reconsideration,
  legacy-unclassified, decision idempotency, and recurrence changeset replay.
- The story verification command runs the targeted suite and the committed
  changeset rebuild validator.
