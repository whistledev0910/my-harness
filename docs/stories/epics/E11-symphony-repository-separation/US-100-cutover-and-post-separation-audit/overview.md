# Overview

## Current Behavior

Until cutover, repository-harness remains the working source and the Symphony
target is a proven candidate. Merging the source deletion first would create a
window with no canonical working Symphony. Publishing the target without final
cross-release proof could declare an incompatible product complete.

## Target Behavior

The target is merged/published first, source cleanup second, then one released
Symphony artifact operates against one cleaned released/installed Harness. Both
repositories publish canonical ownership, and local core durable state no
longer surfaces active/runnable Symphony work. Completed allowlisted E11
receipt proxies may remain visible as migration history.

## Affected Users

- Maintainers and contributors of both repositories.
- Operators installing Harness and Symphony.
- Agents following repository-local docs and durable work queues.

## Affected Product Docs

- Both root READMEs and changelogs.
- Decision `0009` and completed E11 evidence.
- Symphony provenance and compatibility docs.

## Acceptance Criteria

- The Symphony target default branch contains the reviewed provenance import,
  standalone workspace, protocol adapter, docs, parity suite, and release
  workflow.
- A Symphony version/tag and artifact checksums are recorded before the source
  cleanup merge.
- Repository-harness cleanup/regression PR is merged only after target release
  artifacts are retrievable and verified.
- The cleaned Harness default branch completes its normal post-merge release;
  the exact immutable CLI tag, source SHA, platform artifact set, and checksums
  are recorded before the final cross-repository smoke.
- Compatibility is proven against two named Harness releases: the initial
  protocol-v1 tag produced by `US-092` and the later cleaned-core tag produced
  after `US-099`. The test reads each release's contract JSON and records the
  tuple; it never infers compatibility from semver ordering.
- A clean temporary Harness install from the cleaned release passes its own
  smoke suite.
- The released Symphony artifact runs from outside both clones and passes
  doctor, work list, prepare, deterministic execution, Web health/UI, and sync
  first against an initial-tag fixture and then against the cleaned Harness
  install. The cleaned fixture uses the explicit checksum-verified CLI upgrade
  path when replacing the initial binary.
- Repository descriptions/docs identify the correct canonical owners and link
  only through the versioned runtime relationship.
- Repository-harness matrix, backlog, tools, audit, improvement health, and
  proposals show no active Symphony story/provider/suggestion.
- Symphony target state shows no active core E09/E10/E11 work imported as its
  product backlog.
- All registered legacy worktrees are reviewed. Dirty work is committed,
  archived as patches/bundles, or explicitly discarded with evidence before
  `git worktree remove`/`prune`; no recursive directory deletion is used.
- Local run artifacts are archived only after secret/path review or discarded
  explicitly; old `.symphony/state.db` is not activated in the target.
- The source checkout's ignored `.impeccable/**` personal consent/config is
  inspected for secrets, then archived outside the active checkout or deleted
  per the recorded owner disposition. The cutover audit requires no remaining
  `.agents`, `.codex`, or `.impeccable` directory in either active product
  checkout.
- Rollback is rehearsed or mechanically verified: source tag/bundle restores
  the old workspace, target raw-import tag rebuilds the target, and DB backups
  restore their matching replay epochs.
- The observation window is owned by `hoangnb24` and lasts at least seven
  calendar days after the released cross-repo smoke and through one complete
  real development/use cycle, whichever is later. Blocking signals are any
  protocol mismatch, state loss/duplication, installer/release regression,
  wrong-owner active suggestion, or rollback-required platform failure.
- `US-100` remains `in_progress` and rollback artifacts remain retained until
  the observation window closes with no blocking signal; only then may explicit
  story completion mark the epic implemented.
- Every blocking-signal class has the concrete recovery in the exec plan
  (compatible release tuple, paired state epoch, installer/release revert,
  selector ownership fence, or platform artifact withdrawal). Any repair
  restarts the entire observation window; elapsed pre-repair days do not count.

## Non-Goals

- Continue dual development after canonical cutover.
- Force-push either established default branch.
- Delete historical tags, bundles, PRs, or approved archives.
- Claim desktop signing/notarization if it was deferred by `US-096`.
