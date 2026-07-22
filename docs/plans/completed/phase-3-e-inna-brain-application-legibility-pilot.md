# Phase 3 Pilot: e-inna-brain Application Legibility

Date: 2026-07-21

## Status

Completed at the human-judgment blocker

## Outcome

Use a fresh `e-inna-brain` Git worktree and Herdr-controlled coding agents to
evaluate whether the reduced Phase 1+2 Harness core helps an agent implement
and validate this real application task:

> Add rate-limiting to the `/chat` endpoint.

The pilot must preserve the original checkout, install the latest core-only
Harness into the pilot worktree, record what the agents were given and what
they discovered, and stop at the first blocker that genuinely requires human
product or operational judgment. The final form of this file is the Phase 3
evidence report.

## Context

- `docs/WORKFLOW.md` defines the repository-centered default workflow.
- `docs/decisions/0019-repository-centered-default-workflow.md` removes the
  SQLite lifecycle from the ordinary task path.
- `docs/plans/completed/phase-2-knowledge-boundary-and-payload-reduction.md`
  records the ten-file core-only installation boundary.
- OpenAI Harness Engineering is the anchor: a small repository map, direct use
  of application and development tools, observable validation, and mechanical
  invariants should reduce human attention.
- Source consumer repository: `/Users/tubakhuym/projects/e-inna-brain`.
- Frozen starting revision: `9be2b9b624f29c2c4f93bb576485fd8de2085af4`
  (`develop`).
- The source checkout is intentionally not used because it contains unrelated
  untracked files: `.harness-backup/` and
  `docs/operations/production-environment-cost-guide.md`.
- An older unrelated Herdr worktree on branch `agent/phase5-pilot-einna` is
  preserved and not reused.

## Scope

In scope:

- Create one new Herdr-managed `e-inna-brain` worktree from the frozen revision.
- Use Herdr-controlled agents for every content modification in that worktree.
- Install the current core-only Harness from this repository without selecting
  the optional Rust CLI/SQLite bundle.
- Give the implementation agent the task text exactly as written above, plus
  only the normal repository/worktree context an agent would receive.
- Observe discovery, planning, implementation, validation, use of application
  signals, and requests for human judgment.
- Record prompts, agent output, commands/evidence reported by agents, repository
  diffs, validation results, interventions, and blockers in this file.
- Preserve recoverability: the pilot branch/worktree may be discarded without
  modifying the original checkout or branch.

Out of scope:

- The orchestrator directly editing application, test, configuration, or
  Harness files in `e-inna-brain`.
- Cleaning or changing either existing `e-inna-brain` checkout/worktree.
- Using the compatibility SQLite lifecycle unless an explicit external
  orchestrator contract requires it.
- Inventing the rate limit, identity key, deployment topology, or user-facing
  error contract when the repository does not already decide them.
- Merging, pushing, deploying, or mutating production infrastructure.
- Generalizing one pilot into a claim that every application is agent-legible.

## Approach

1. Establish the starting repository, worktree, Herdr, and instruction state.
2. Create a new named worktree and Herdr workspace.
3. Delegate the core-only Harness installation to a Herdr-controlled agent.
4. Verify the installed payload, legacy preservation behavior, and absence of
   new CLI/SQLite prerequisites.
5. Delegate the frozen `/chat` rate-limiting task to a fresh Herdr-controlled
   implementation agent.
6. Observe without supplying unstated product decisions. Provide repository
   navigation help only when the information already exists and the failure is
   a tooling/discovery issue; record every such intervention.
7. Let the agent implement and validate until it either produces relevant
   executable/observable evidence or identifies a blocker requiring human
   judgment.
8. Audit the evidence against the Phase 3 questions and record the result.

## Risks And Recovery

- **Dirty source checkout:** never install into or edit the original checkout.
  Recovery is removal of only the new pilot worktree/branch after review.
- **Agent changes outside the worktree:** launch every agent with the exact
  worktree as its current directory and verify all resulting paths with Git.
- **Legacy Harness replacement:** install with merge/refresh semantics and
  inspect the diff; preserve consumer-owned product, operation, and decision
  material.
- **Accidental compatibility activation:** do not pass `--with-cli`, do not
  bootstrap, and verify that no new database or CLI dependency is introduced.
- **Ambiguous rate-limit policy:** stop instead of selecting limits, identity,
  storage consistency, response shape, or trust-proxy behavior without existing
  product authority.
- **External side effects:** keep validation local; do not deploy, push, or call
  paid/live providers unless the user separately authorizes it.

## Phase 3 Questions

1. Can the agent discover the current product and architecture contract from
   the reduced core map?
2. Can it identify the `/chat` boundary, existing tests, and application startup
   path without human file-by-file direction?
3. Can it determine the rate-limit behavior from existing repository truth, or
   does product intent remain genuinely ambiguous?
4. Can it run focused validation locally without relying on Harness proof
   metadata?
5. Can it operate or observe the real application sufficiently to validate the
   HTTP behavior?
6. Which missing capability causes the first human intervention or blocker?
7. Did the core reduce ceremony without hiding a real product or proof gap?

## Evidence Ledger

### E0 — Initial State

- `repository-harness` revision: `10a813593633b8c17a192be6906782eec639d2bd`.
- `e-inna-brain` starting branch/revision:
  `develop` / `9be2b9b624f29c2c4f93bb576485fd8de2085af4`.
- Original `e-inna-brain` checkout: dirty only with the two untracked paths
  listed in Context; preserved.
- Existing Herdr `e-inna-brain` worktree:
  `agent/phase5-pilot-einna`; preserved.
- Herdr: version `0.7.4`, protocol `16`, server running and compatible.
- Pilot worktree:
  `/Users/tubakhuym/.herdr/worktrees/e-inna-brain/agent-phase3-application-legibility-einna`,
  branch `agent/phase3-application-legibility-einna`, Herdr workspace `w2J`,
  created from the frozen revision above.

### E1 — Core Installation Agent

- Herdr agent: `phase3-core-installer`, pane `w2J:p2`, launched in the pilot
  worktree with the absolute Codex executable path required by the Herdr server
  environment.
- Exact prompt:

  > Read /Users/tubakhuym/projects/repository-harness/docs/plans/active/phase-3-e-inna-brain-application-legibility-pilot.md. You are the Phase 3 core-installation agent. Execute Approach step 3 and the E1 evidence requirements only. Work only in your current e-inna-brain worktree. Do not investigate rate limiting. Do not use with-cli, bootstrap SQLite, commit, push, deploy, or change the original checkout. Stop on ambiguity and report exact commands, changes, validation, and interventions.

- The old consumer instructions first directed the agent to legacy Harness
  reference material and a matrix check. The referenced
  `scripts/bin/harness-cli` did not exist. The agent treated that as pre-install
  evidence and did not bootstrap a CLI or database to satisfy the stale
  ceremony.
- After reading the current installer guidance, the agent selected merge and
  agent-shim refresh semantics. It first ran:

  ```text
  /Users/tubakhuym/projects/repository-harness/scripts/install-harness.sh --directory /Users/tubakhuym/.herdr/worktrees/e-inna-brain/agent-phase3-application-legibility-einna --merge --refresh-agent-shim --yes --dry-run
  ```

  It then ran the same command without `--dry-run`.
- The installer selected the core profile, skipped the optional CLI source,
  created five files, updated only the marked Harness block in `AGENTS.md`, and
  skipped five existing consumer-owned files.
- Created core files:
  `docs/WORKFLOW.md`, `docs/plans/README.md`,
  `docs/plans/active/README.md`, `docs/plans/completed/README.md`, and
  `docs/templates/exec-plan.md`.
- Recovery evidence: the previous `AGENTS.md` was copied to
  `.harness-backup/20260721140715/AGENTS.md`.
- Verification reported by the agent:
  all ten core paths are present; the five newly created payload files match
  the source revision; the canonical `AGENTS.md` Harness block matches the
  source; the backup matches the frozen base; four pre-existing core files were
  preserved byte-for-byte; legacy docs, schemas, and `.gitignore` were
  unchanged; no database, CLI binary, or bootstrap script was created; and
  `git diff --check` passed.
- Before and after, `harness.db`, `scripts/bin/harness-cli`, and both legacy
  bootstrap script paths were absent. The refresh therefore did not turn the
  compatibility SQLite/CLI path into a prerequisite.
- The original checkout remained unchanged, with only its two pre-existing
  untracked paths. No commit, push, deployment, SQLite operation, or live
  provider call occurred.
- Human interventions: none. The agent completed in 2 minutes 58 seconds.

### E2 — Rate-Limiting Agent

- Herdr agent: `phase3-rate-limit-agent`, pane `w2J:p3`, launched as a fresh
  Codex session in the pilot worktree.
- Exact task prompt, with no added implementation policy:

  > Add rate-limiting to the /chat endpoint

- The agent followed the refreshed entry path: it read `AGENTS.md`, then
  `docs/WORKFLOW.md`, inspected the repository map, and located the NestJS
  controller, runtime configuration/module wiring, application bootstrap, and
  chat/runtime/bootstrap contract tests without human file-by-file direction.
- `rg` was unavailable in the agent environment. It disclosed the tooling
  failure, substituted targeted `find`/`grep` inspection, and continued without
  requesting intervention. Unrelated MCP startup failures for Exa, shadcn, and
  the sites design picker did not affect repository discovery.
- The agent found the stable JSON/SSE `/chat` contract and no existing
  throttling library or inbound `/chat` quota policy. It then searched product
  and architecture material for quota, identity, proxy, and client-address
  rules.
- The repository confirms that inbound rate-limit behavior is undecided:
  `SPEC.md` defines `/chat` request, JSON/SSE success, and existing failure
  behavior but no 429 contract or quota. Its open rate-limit question concerns
  outbound E-INNA GET APIs, not inbound `/chat`. The existing boundary error
  types accept only status 400, 401, or 500 and codes `BAD_REQUEST`,
  `UNAUTHORIZED`, or `INTERNAL_ERROR`.
- After explicitly stating that no quota was specified, the agent proposed:
  20 admitted requests per 60 seconds, keyed by `(instanceId, userId)`, using a
  sliding window, with request 21 returning 429 `RATE_LIMITED` and
  `Retry-After`. It also chose endpoint isolation from health, metrics, and
  webhooks.
- Those are coherent candidate semantics, but they are not repository-
  authorized. They decide quota, time algorithm, identity/trust boundary,
  response schema, and admission semantics. The agent therefore crossed the
  workflow's human-judgment boundary after discovering it.
- Orchestrator intervention: one. The agent was interrupted with Escape before
  it edited application code. Worktree status afterward contained only the E1
  Harness refresh. No application, test, package, or runtime configuration
  file changed and no validation command ran.

### E3 — Blocker Or Completion Boundary

The first blocker is product and operational intent, not code discovery.

The repository does not decide:

1. the allowed request count, window, or burst behavior;
2. whether the key is instance, user, conversation, authenticated caller,
   source address, or a combination, and whether request-body identifiers are
   trusted for abuse control;
3. whether limits must be shared across replicas and survive restarts, which
   decides in-process versus shared storage;
4. when long-lived SSE requests consume or release capacity;
5. the public 429 body/code and `Retry-After` contract; or
6. whether enforcement belongs in this NestJS service or an upstream E-INNA
   proxy/gateway.

Cause and effect: choosing any implementation now would silently turn an agent
guess into product policy. For example, the proposed `(instanceId, userId)` key
avoids grouping many users behind one proxy address, but a caller able to vary
`userId` can evade it; an in-memory sliding window is simple, but each service
replica would grant a separate allowance and a restart would erase it; adding
429 requires expanding the currently closed error status/code union and
therefore changes the public API contract. Human direction is required before
implementation and behavior-appropriate tests can be written.

## Phase 3 Audit At Pause

1. **Product and architecture discovery: passed.** The agent reached the
   relevant current contracts through the reduced map. It did not need the old
   SQLite story, matrix, trace, or scoring lifecycle.
2. **Application-boundary discovery: passed.** The agent found the controller,
   configuration and module seams, bootstrap, and adjacent tests without human
   navigation.
3. **Behavior determination: correctly exposed a gap.** The repository defines
   `/chat` but not inbound throttling semantics. The old roadmap's rate-limit
   item is for outbound E-INNA API calls and cannot authorize an inbound policy.
4. **Focused local proof: not reached.** Tests cannot be meaningfully authored
   until the missing policy is decided.
5. **Real HTTP observation: not reached.** There was no authorized behavior to
   exercise. This is not evidence of runtime illegibility.
6. **First intervention: policy-boundary enforcement.** Tooling failures were
   self-recovered; a human had to stop the agent when it converted ambiguity
   into defaults.
7. **Ceremony result: reduced, with one remaining weakness.** The new core
   removed control-plane ceremony and made the real code/tests visible, but a
   prose pause rule was not strong enough to reliably prevent speculative
   product design.

## Progress

- [x] Inspect repository status, existing worktrees, instructions, and Herdr.
- [x] Freeze the pilot task and starting revision.
- [x] Create the Git-native Phase 3 plan and evidence ledger.
- [x] Create the isolated Herdr worktree.
- [x] Install and verify the core-only Harness through a Herdr agent.
- [x] Run the rate-limiting task through a fresh Herdr agent.
- [x] Record the blocker or validated implementation boundary.
- [x] Audit the evidence available at the blocker boundary.
- [x] Close the pilot at the user-requested human-advice boundary.

## Decisions

- 2026-07-21: Use one evolving Git-native plan as both the execution plan and
  evidence report so the pilot does not recreate parallel story, trace, and
  validation records.
- 2026-07-21: Base the pilot on the current `develop` commit while preserving
  untracked source-checkout content by using a separate worktree.
- 2026-07-21: All `e-inna-brain` content changes, including Harness installation,
  must be made by Herdr-controlled agents; the orchestrator may inspect state,
  create the requested worktree, capture evidence, and control agents.
- 2026-07-21: Stop rather than invent rate-limit product semantics that are not
  already authoritative in the consumer repository.

## Validation

- **New-worktree proof:** the pilot branch and worktree remain at the frozen
  revision `9be2b9b624f29c2c4f93bb576485fd8de2085af4`; Herdr agents
  `phase3-core-installer` and `phase3-rate-limit-agent` both ran there.
- **Core-refresh proof:** all ten reduced-core paths were present after install;
  payload and backup comparisons passed; no Rust CLI, SQLite database, or
  bootstrap path was introduced.
- **Delegation proof:** the implementation agent received the exact frozen task
  and its transcript records discovery, candidate policy, and interruption.
- **No-application-change proof:** final pilot status contains only the core
  refresh paths (`AGENTS.md`, `.harness-backup/`, `docs/WORKFLOW.md`,
  `docs/plans/`, and `docs/templates/exec-plan.md`). No source, test, package,
  or runtime configuration path changed.
- **Isolation proof:** the original checkout remains on `develop` at the same
  frozen revision with only its two pre-existing untracked paths.
- **Behavior proof boundary:** focused `/chat` tests and live HTTP exercise were
  intentionally not run because the repository does not authorize a behavior
  to implement. Claiming such proof would require inventing the missing policy.

## Result

Paused at the first human-judgment boundary. The reduced core successfully made
the repository and proof surfaces discoverable with no SQLite/CLI lifecycle and
no navigation intervention. It did not by itself prevent a capable agent from
inventing missing product semantics: after finding the gap, the agent selected
an arbitrary but plausible policy instead of pausing. No rate-limiting code was
accepted. This is the terminal state requested for this pilot: stop when human
advice is needed. A later task may decide the six E3 contract and topology
questions, record that decision as repository truth, and start a fresh
implementation attempt.
