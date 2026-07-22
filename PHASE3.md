# Reduction Phase 3 — Application Legibility Pilot

## Status

Active. The first real-consumer evidence checkpoint is complete; the full
runtime and interface loop is not yet proven.

Phase 1 made the repository-centered workflow authoritative. Phase 2 reduced
the default installation to the ten-file core and explicitly deferred
application-legibility claims. Decision
`docs/decisions/0021-consumer-first-application-legibility-phase.md` defines the
Phase 3 boundary and evidence standard.

The historical plan that used the Phase 3 name for mandatory trace scoring,
friction queries, and backlog operations is preserved at
`docs/compatibility/phase-3-active-observability-legacy.md`. It is compatibility
history, not the default workflow.

## Anchor

OpenAI's
[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
describes an agent environment where repository knowledge, development tools,
application operation, validation, feedback, and recovery are directly
accessible. At higher autonomy, an agent can reproduce a bug, operate the
application, implement a fix, verify through the application, recover from
failures, and escalate only when judgment is required.

That behavior depends on repository-specific structure and tooling. Phase 3
therefore tests one real vertical path and does not claim universal legibility.

## Target Outcome

Prove that a fresh agent can take one real application task through this loop:

```text
discover how to run the application
-> start an isolated worktree-local instance
-> create deterministic scenario state
-> reproduce through the real user/API interface
-> inspect relevant runtime evidence
-> implement the bounded change
-> run focused executable proof
-> verify through the same interface
-> stop and clean up only that instance
```

A genuine product or operational authority gap stops the run before edits. That
stop is useful evidence, but it proves only the capabilities exercised before
the stop.

## First Consumer: e-inna-brain

Consumer revision:
`9be2b9b624f29c2c4f93bb576485fd8de2085af4` (`develop`).

Frozen task:

> Add rate-limiting to the `/chat` endpoint.

The consumer is a real NestJS application and the task reaches a public API
boundary. The repository defines `/chat` JSON/SSE behavior but does not define
an inbound rate-limit quota, trusted identity, shared-state topology, SSE
admission semantics, enforcement owner, or public 429 contract.

### Baseline run

The reduced core installed in a fresh worktree without adding the Rust CLI or a
SQLite database. A fresh agent found the controller, module wiring, runtime
configuration, bootstrap, deployment proxy, product contract, and adjacent
tests without human navigation.

After correctly finding the missing policy, it invented 20 requests per 60
seconds per `(instanceId, userId)`, a sliding window, and a new
`RATE_LIMITED`/`Retry-After` contract. The orchestrator interrupted it before an
application edit.

### Core correction

The installed authority gained one compact rule:

> Before editing, identify repository authority for each new externally
> observable policy. If materially different choices remain open, stop before
> edits; configurable defaults are not authority.

The workflow adds a discriminating example: unspecified rate limiting must
stop; a documented quota and trusted key may proceed. Mandatory entry context
remains within the existing limits: a 1,590-byte installed authority block and
998 words across `AGENTS.md` plus `docs/WORKFLOW.md`.

### Clean replay

A second clean worktree received the committed core. A new agent received only
the exact frozen task. It found the same application surfaces and missing
policy, explained how `userId` versus `instanceId` keys allocate capacity
differently and how in-memory state resets and multiplies across replicas, then
stopped without editing or orchestrator intervention.

Observed transition:

```text
baseline: find policy gap -> invent configurable defaults -> human interruption
replay:   find policy gap -> explain consequences -> stop with no app diff
```

This proves repository discovery and decision-boundary improvement. It does not
prove runtime application legibility.

## Evidence Matrix

| Workstream | Required evidence | e-inna result | Status |
| --- | --- | --- | --- |
| P3-01 Select consumer and freeze task | Real consumer, fixed task/outcome, baseline interventions | Consumer, revision, prompt, transcripts, and one intervention are frozen; the task is a new policy feature rather than a reproducible defect | Partial |
| P3-02 Worktree-local execution | Two simultaneous isolated runtimes, ports, state, logs, and independent stop | Two Git worktrees were isolated; no application process was started | Not proven |
| P3-03 Deterministic reproduction | Known identity/state, repeatable scenario, idempotent reset | No fixture or scenario was created because policy authority was missing | Not proven |
| P3-04 Runtime evidence | Visible failure correlated to instance-local logs or signals | Source and deployment configuration were discovered; no runtime log was produced or queried | Not proven |
| P3-05 Agent-operable interface | Discoverable URL/request/auth and reproduction through the real surface | `/chat` route and contract were found; no HTTP request exercised the running service | Partial discovery only |
| P3-06 Behavior to focused proof | Focused rule test plus appropriate broader proof | Adjacent tests were found; no authorized behavior existed to test | Not proven |
| P3-07 Repeat improved task | Same task replayed; compare interventions, runtime, before/after proof, isolation, cleanup | Exact prompt replay reduced policy-boundary interventions from one to zero; runtime/interface loop remained unentered | Partial |

## Durable Evidence

- `docs/plans/completed/phase-3-e-inna-brain-application-legibility-pilot.md`:
  baseline, prompts, installation, discovery, invented policy, intervention, and
  blocker.
- `docs/plans/completed/phase-3-decision-boundary-replay.md`: core correction,
  validation, local source commit, clean installation, exact replay, no-diff
  result, and pass audit.
- `docs/decisions/0021-consumer-first-application-legibility-phase.md`: lasting
  phase scope, evidence boundary, and completion rule.

These artifacts are Git-native evidence. No parallel intake, story, matrix,
trace-score, audit, or proposal state is required.

## What Is Proven

1. The reduced core can be installed into a brownfield application without
   reintroducing mandatory CLI/SQLite ceremony.
2. A fresh agent can navigate from the compact map to relevant product,
   architecture, deployment, code, and test truth without human file guidance.
3. Application legibility includes recognizing absent authority, not merely
   finding an implementation seam.
4. One compact rule and concrete example changed the observed agent behavior
   from speculative policy to a self-directed stop.
5. The result is reproducible for this task, model, repository revision, and
   local environment; it is not a universal reliability claim.

## What Remains To Prove

1. Two application instances can run simultaneously in separate worktrees with
   isolated ports, writable state, logs, process identity, and cleanup.
2. A deterministic, fixture-only scenario can reproduce known behavior from a
   fresh instance.
3. An agent can move from an interface-visible failure to relevant runtime
   evidence without human operational guidance.
4. The selected API, browser, desktop, mobile, or CLI surface is directly
   operable by the agent.
5. The agent can implement an authorized fix, run the smallest focused proof,
   and verify before/after behavior through the same interface.
6. Startup failures, application failures, readiness, and recovery are
   distinguishable and instance-local.

## Next Evidence Gate

Select one real consumer task whose expected behavior is already authoritative
and locally exercisable. Record the existing reproduction path before improving
the environment.

The next run should capture:

- startup commands and failures;
- undocumented human explanations;
- port, process, data, and log isolation;
- deterministic state creation/reset;
- interface-level before evidence;
- runtime evidence used to locate the cause;
- focused and broader executable proof;
- interface-level after evidence; and
- independent stop and cleanup.

Phase 3 completes only when one task exercises that loop with trustworthy
evidence, including zero undocumented setup interventions, or when a later
accepted decision changes the exit condition based on new observations.

## What Phase 3 Must Not Become

- A generic observability platform.
- A new application-legibility database or capability registry.
- A maturity ladder or Harness compliance dashboard.
- Generic browser automation bundled into every consumer.
- A universal start command imposed on every stack.
- Automated PR orchestration as a substitute for application proof.
- Five hypothetical adapters before one real vertical path works.
- A replacement for the optional SQLite compatibility layer.

The order is evidence-first:

```text
observe one real task
-> expose only missing capabilities
-> rerun the frozen task
-> keep what reduces human intervention
-> extract a small reusable pattern
```

Most Phase 3 implementation belongs in the consumer: stack-natural runtime
commands, fixtures, readiness, instance-local logs, interface support, tests,
and development documentation. `repository-harness` receives reusable knowledge
only after consumer evidence proves it.
