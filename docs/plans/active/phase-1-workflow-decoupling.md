# Phase 1 Workflow Decoupling

Date: 2026-07-20

## Status

Accepted and ready for implementation. No implementation work has started.

## Anchor

Phase 1 is anchored to OpenAI's
[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/).

The anchor treats human time and attention as the scarce resource. It favors a
short repository map, structured in-repository knowledge, direct access to the
application and its development tools, durable execution plans for complex
work, mechanical enforcement of important invariants, and recurring targeted
garbage collection.

Phase 1 applies those principles by removing the mandatory operational ledger
from the default task path without deleting its implementation or historical
state.

## Outcome

Replace the database-centered default task lifecycle with repository-centered
workflows:

```text
bounded change
  -> small repository map
  -> relevant product, design, code, and tests
  -> implementation
  -> executable or observable proof
  -> concise outcome report

complex or multi-session change
  -> one Git-native active execution plan
  -> implementation with progress and decision updates
  -> executable or observable proof
  -> completed plan plus any lasting design decision
```

After Phase 1, ordinary bounded changes require no Harness CLI mutation.
Existing intake, story, trace, scoring, audit, proposal, SQLite, changeset, and
orchestration behavior remains available for compatibility but is not part of
the default repository workflow.

## Safety Invariants

Phase 1 must preserve these behaviors:

1. Answer, review, diagnosis, plan, explanation, and status requests remain
   read-only.
2. Agents determine the requested outcome and relevant repository truth before
   editing.
3. Completion requires behavior-appropriate executable or observable proof.
4. Agents pause when product intent is ambiguous, an action is difficult to
   recover, validation would be weakened, or additional authority is needed.
5. Complex work remains resumable through a Git-native execution plan.
6. Lasting product and architecture decisions remain repository-visible and
   indexed.
7. Existing databases, semantic changesets, CLI commands, and external
   orchestration contracts remain readable and compatible throughout Phase 1.

## Current Behavior

The current change workflow requires bootstrap, durable intake, matrix
retrieval, lane-specific context, story and proof records for normal or
high-risk work, manual trace recording, and optional friction/backlog updates.
Several of these records measure whether an agent described the process rather
than whether the resulting application behavior is correct.

The same tiny/normal/high-risk lane also controls unrelated questions:

- whether work needs durable memory;
- whether human judgment is required;
- how much context should be read;
- which documents must be created; and
- what validation is appropriate.

This creates ceremony on bounded tasks and false equivalence between changes
that share a risk keyword but have different consequences.

## Target Work Selection

Phase 1 replaces the single lane with three independent questions.

### Durable Memory

Use an ephemeral plan for bounded, single-session work.

Create or update one file under `docs/plans/active/` when work:

- is likely to span sessions;
- requires coordination across agents or contributors;
- has meaningful dependencies or an important execution sequence;
- needs an explicit recovery procedure; or
- would be unsafe or expensive to resume from the diff alone.

### Human Judgment

Pause only when:

- product intent is ambiguous;
- valid alternatives have materially different product consequences;
- the action is irreversible or difficult to recover;
- validation, security, or compatibility requirements would be weakened; or
- the requested work does not authorize the necessary action.

Sensitive subject matter alone does not require a pause when the expected
behavior and authority are already explicit.

### Validation

Select proof from the affected behavior:

- focused tests for local rules;
- integration tests for persistence or service boundaries;
- end-to-end interaction for user-visible behavior;
- recovery rehearsal for migrations and destructive operations; and
- runtime measurements for reliability or performance claims.

Harness status fields and proof flags are not completion evidence by
themselves.

## Scope

### In Scope

- Replace the mandatory task lifecycle in `AGENTS.md` and the canonical Harness
  operating guidance.
- Introduce a compact repository-centered workflow and plan-selection rule.
- Establish `docs/plans/active/` and `docs/plans/completed/` as the durable work
  memory for complex tasks.
- Add one reusable execution-plan template.
- Mark database-centered lifecycle documents and commands as compatibility or
  legacy surfaces where they are no longer authoritative.
- Keep the small agent entrypoint, repository knowledge indexes, durable design
  decisions, proof-before-completion, and human judgment gates.
- Update Bash, PowerShell, Claude, installer, documentation-contract, and task
  evaluation surfaces so fresh installs expose the same default workflow.
- Define an explicit opt-in refresh path for existing installations.
- Validate the reduced workflow on representative read-only, bounded, complex,
  user-visible, and judgment-requiring tasks.

### Out of Scope

- Delete or rewrite existing SQLite databases.
- Remove CLI commands, schema migrations, semantic changesets, snapshots, or
  historical records.
- Break or migrate Symphony's orchestration protocol.
- Refactor the Rust CLI implementation.
- Build Phase 2 application-legibility capabilities such as browser control,
  worktree-local observability, or generated application maps.
- Move all historical evidence to a separate archive.
- Claim that optional control-plane features are permanently removed before a
  compatibility and usage window has passed.

## Control Transfer

Phase 1 removes obligations only after naming their repository-centered
replacement.

| Current control | Phase 1 replacement |
| --- | --- |
| Intake row | Requested outcome in working context or the active execution plan |
| Risk lane | Independent durable-memory, human-judgment, and validation decisions |
| Story status | Active/completed plan location and Git history |
| Proof matrix flags | Actual test, CI, application, or runtime evidence |
| Manual task trace | Git diff, PR history, test artifacts, and plan progress |
| Context score | Indexed repository knowledge plus link/freshness checks |
| Entropy audit | Repository-specific mechanical checks and targeted cleanup |
| Friction proposal | Direct bounded repair or ordinary technical-debt entry |
| Decision database row | Indexed, Git-native durable decision document |

## Workstreams

### 1. Authority And Source Hierarchy

- [ ] Make the compact agent entrypoint and canonical workflow document the
      current authority.
- [ ] Preserve the read-only request boundary.
- [ ] State that compatibility documentation cannot reintroduce mandatory
      lifecycle steps.
- [ ] Define how product, design, plan, generated, and historical documents are
      indexed and retrieved.

### 2. Default Workflows

- [ ] Document the bounded-change flow.
- [ ] Document the durable-plan flow.
- [ ] Document the human-judgment overlay.
- [ ] Replace lane-driven validation with behavior-driven proof selection.
- [ ] Require concise final reporting of outcome, changed surfaces, proof, and
      unresolved limitations.

### 3. Durable Plan Structure

- [ ] Add `docs/plans/README.md`.
- [ ] Add `docs/plans/completed/`.
- [ ] Add a single reusable execution-plan template.
- [ ] Define the active-to-completed transition.
- [ ] Define when a plan decision must be promoted into `docs/decisions/`.

### 4. Legacy And Compatibility Boundaries

- [ ] Identify every document that presents intake, story, matrix, trace,
      scoring, audit, or proposal operations as mandatory.
- [ ] Add clear compatibility banners or relocate historical guidance without
      deleting it.
- [ ] Keep existing CLI behavior and machine contracts unchanged.
- [ ] Confirm that external orchestration consumers retain their current paths.

### 5. Installation And Refresh

- [ ] Make fresh installations use the repository-centered workflow by default.
- [ ] Provide an explicit, backed-up refresh path for existing agent shims.
- [ ] Keep existing databases and historical documents untouched during refresh.
- [ ] Keep Bash, PowerShell, and Claude instruction surfaces equivalent.

### 6. Validation And Evaluation

- [ ] Update documentation-contract tests to reject stale mandatory lifecycle
      instructions on the default path.
- [ ] Preserve all existing CLI and orchestration compatibility tests.
- [ ] Exercise one read-only task.
- [ ] Exercise one bounded documentation change.
- [ ] Exercise one bounded code fix with existing expected behavior.
- [ ] Exercise one user-visible fix requiring application interaction.
- [ ] Exercise one multi-session change using a durable plan.
- [ ] Exercise one consequential ambiguous change that must pause for judgment.
- [ ] Compare required Harness commands, initial Harness context, human
      intervention, validation quality, and false-completion behavior.

## Compatibility Strategy

Phase 1 follows these rules:

```text
stop requiring old writes
  -> keep old reads and commands
  -> validate the new default workflow
  -> migrate optional consumers later
  -> delete dead implementation only in a later decision
```

- Existing CLI releases and databases remain supported.
- No schema migration is introduced for workflow decoupling.
- No historical state is rewritten to resemble the new model.
- Fresh installations adopt the new default.
- Existing installations change only through an explicit refresh or upgrade.
- A compatibility failure blocks Phase 1 completion but does not authorize
  weakening the reduced workflow.

## Rollback

Before CLI or data removal exists, Phase 1 can be rolled back by restoring the
prior agent and operating instructions. Existing commands and durable state
remain intact, so rollback does not require reconstructing deleted data or
releasing a replacement database format.

Rollback is appropriate if representative tasks show:

- an increase in unsupported completion claims;
- loss of necessary coordination or resumability;
- repeated inability to find relevant repository truth;
- an external orchestration compatibility regression; or
- more human attention rather than less.

Rollback should restore only the minimum old obligation needed to address the
observed failure. It must not automatically restore the entire lifecycle.

## Acceptance Criteria

- A bounded change requires zero Harness CLI commands.
- Initial mandatory Harness context is no more than a compact repository map and
  workflow, targeting under approximately 1,000 words.
- Complex work uses one evolving active plan rather than parallel story,
  overview, design, execution, validation, trace, and decision records.
- Completion is supported by relevant executable or observable proof.
- Judgment gates depend on ambiguity, recoverability, validation strength, and
  authority rather than a risk-keyword count.
- Fresh Bash, PowerShell, and Claude installations expose the same default
  workflow.
- Existing CLI, database, changeset, release, and orchestration compatibility
  checks continue to pass.
- Existing durable state remains readable and is not rewritten.
- Default-path documentation contains no contradictory mandatory control-plane
  lifecycle.
- Representative task evaluation shows reduced Harness commands and context
  without increased false completion or human intervention.

## Validation

Implementation must identify focused commands as the affected files become
known. Final validation must include:

```text
documentation contract and stale-guidance checks
installer mode and agent-shim parity checks
representative task evaluations
existing orchestration protocol checks
existing pre-merge repository contract
Git diff and generated-artifact review
```

Passing Harness status or trace scores are explicitly not Phase 1 evidence.

## Decision Log

- 2026-07-20: OpenAI Harness Engineering is the anchor for the reduced workflow.
- 2026-07-20: Preserve repository knowledge, durable complex plans, mechanical
  invariants, application legibility, and targeted garbage collection.
- 2026-07-20: Remove the operational ledger from the default path before
  deleting any implementation or state.
- 2026-07-20: Use independent durable-memory, human-judgment, and validation
  decisions instead of one tiny/normal/high-risk lane.
- 2026-07-20: Record Phase 1 with one Git-native plan and decision, intentionally
  without intake, story, matrix, trace, backlog, or decision-database writes.
- 2026-07-20: Decision `0019-repository-centered-default-workflow` governs the
  target behavior. The current default does not change until implementation is
  completed and validated.

## Progress

- [x] Review the existing repository and identify the seven principal weaknesses.
- [x] Read and adopt OpenAI Harness Engineering as the anchor.
- [x] Agree on the Phase 1 boundary and reduced workflow.
- [x] Record the durable direction in decision `0019`.
- [ ] Begin implementation.
- [ ] Validate representative tasks and compatibility.
- [ ] Move this plan to `docs/plans/completed/` with the final result.

## Result

Not yet implemented.
