# Phase 3 Durable State Publication

Date: 2026-07-21

## Status

Active

## Outcome

Publish an evidence-backed durable Phase 3 state beside the Phase 1 and Phase 2
transitions, push the existing local feature branch, and open a pull request to
`main` without claiming application capabilities that the `e-inna-brain` pilot
did not exercise.

## Context

- OpenAI Harness Engineering describes increasing autonomy through direct
  development/application tools, bug reproduction, application-driven proof,
  feedback loops, and escalation only when judgment is required.
- Decision 0019 established the repository-centered default.
- Decision 0020 reduced the installation to the ten-file core and explicitly
  deferred application-legibility claims until a real consumer supplied
  observable evidence.
- The completed `e-inna-brain` pilot and replay prove repository discovery,
  compatibility decoupling, and correct policy escalation. They do not prove
  runtime startup, deterministic scenario setup, interface reproduction,
  runtime evidence retrieval, implementation, or before/after HTTP proof.
- Local branch `feature/phase3-decision-boundary-replay` contains commits
  `748d35f` and `ccc309c`; neither has been pushed.

## Scope

In scope:

- Add a current decision defining Reduction Phase 3 as a narrow,
  consumer-first application-legibility pilot.
- Reconcile root `PHASE3.md` with the full vertical-loop target and a concrete
  P3-01 through P3-07 evidence matrix.
- Retain the completed e-inna reports as the first evidence checkpoint.
- Make the current status explicit: the checkpoint is complete; the full phase
  remains active until runtime/interface proof exists.
- Update current source indexes and mechanical documentation checks.
- Validate, commit, push the branch, and open a PR to `main`.

Out of scope:

- Inventing the missing e-inna rate-limit policy.
- Modifying either e-inna worktree or checkout.
- Claiming that source discovery equals application operation.
- Adding runtime scripts, fixtures, logs, or generic observability machinery
  without a task that demonstrates the need.
- Merging the pull request.

## Approach

1. Record the lasting Phase 3 scope and evidence boundary in decision 0021.
2. Update `PHASE3.md` to state the end-to-end target and map each workstream to
   observed e-inna proof, missing proof, and the next evidence gate.
3. Link the decision and retained evidence from current source indexes.
4. Add focused doc-contract assertions, then run focused and full repository
   validation.
5. Record validation, commit the durable state, push the existing feature
   branch, and open a PR to `main`.
6. Record the publication evidence here, move this plan to completed, and push
   that final plan-only commit to the PR branch.

## Risks And Recovery

- **Overclaiming Phase 3:** use explicit proved/not-proved rows and keep the
  phase status active until a real application is operated through the full
  loop.
- **Underselling useful evidence:** retain the decision-boundary replay as a
  completed checkpoint with exact before/after behavior and no-diff proof.
- **Core payload pollution:** decision 0021 and phase evidence stay upstream;
  the ten-file consumer profile remains unchanged.
- **External publication error:** inspect the diff and branch commits before
  push; do not merge. A PR can be corrected with follow-up commits.
- **Original checkout contamination:** all edits remain in the dedicated
  Harness worktree.

## Progress

- [x] Reconcile the quoted Phase 3 definition with current e-inna evidence.
- [x] Add decision 0021 and the authoritative evidence matrix.
- [x] Update indexes and documentation contracts.
- [x] Run focused and full validation.
- [ ] Record the result and move this plan to completed.
- [ ] Commit and push the feature branch.
- [ ] Open the pull request to `main`.

## Decisions

- 2026-07-21: Treat the e-inna runs as a completed evidence checkpoint, not as
  proof of the unexecuted runtime/interface loop.
- 2026-07-21: Use the existing unpushed feature branch because it already holds
  the exact core change and replay evidence; creating another branch would
  separate the conclusion from its causal commits.

## Validation

- Focused proof passed: authority parity, documentation contracts, repository
  workflow evaluation, installer profiles, and `git diff --check`.
- Repository proof passed: `scripts/validate-premerge.sh`, including 97 Rust
  tests, formatting, Clippy, protocol/recovery checks, installer profiles,
  documentation/evaluation contracts, and the final pre-merge contract.
- Publication proof: remote branch exists and the PR targets `main` with the
  validated commits.
- Isolation proof: original Harness and e-inna checkouts retain their prior
  revisions and status.

## Result

Pending.
