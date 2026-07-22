# Review Record: Original US-073 Proposal-To-Backlog Lifecycle

> **Review status:** Approved in direction on 2026-07-10 and superseded as the
> execution source by `docs/stories/epics/E09-self-improving-harness-lifecycle/`.
> The original one-story shape was split into dependency-ordered stories
> `US-073` through `US-080`. This file remains historical review evidence.

## 1. Review Purpose

This document turns the agreed Harness workflow into a concrete story shape
before creating the durable story packet.

The review question is simple:

> Does this describe the exact lifecycle we want for an improvement proposal
> from first suggestion through acceptance, implementation, verification,
> closure, and possible later regression?

## 2. Problem

`harness-cli propose` can identify improvement opportunities from backlogs,
traces, frictions, and interventions, but the current lifecycle is not explicit
enough.

That creates several practical problems:

- A suggestion can be repeated after it was already accepted and addressed.
- Closing a backlog item does not clearly tell Harness whether future matching
  evidence is old history or a real regression.
- There is no reliable link from a story to the backlog item it resolves.
- Verification and backlog closure can drift apart.
- Cleanup needs a controlled `--apply` path, but broad mutation would risk
  rewriting historical evidence.
- Similar wording can be mistaken for the same issue unless matching is
  conservative and deterministic.

## 3. Desired Outcome

Harness becomes the governor of its own improvement loop.

For every proposal, Harness can determine whether it is:

- an active suggestion that needs a human decision;
- already accepted and currently being addressed;
- already implemented and therefore suppressed;
- rejected and therefore suppressed unless new evidence needs review;
- a duplicate of an existing open backlog item; or
- a new regression after an earlier item was closed.

The normal lifecycle becomes:

```text
propose
  -> human accepts one specific proposal key
  -> accepted backlog item
  -> story declares the backlog item as resolved or referenced
  -> story verify passes
  -> resolved backlog item closes as implemented
  -> later new evidence either stays suppressed or becomes a regression proposal
```

## 4. Current Behavior

Today, the repository has durable records for stories, backlogs, traces,
frictions, interventions, and verification, but the relationship between those
records is incomplete for this workflow.

The practical consequence is that a proposal may continue to appear because
Harness can see the old evidence but cannot reliably prove that the evidence
was handled by a specific accepted story and verification result.

Historical traces, frictions, and interventions are valuable evidence. They
must remain available for audit and learning rather than being deleted as a
cleanup shortcut.

## 5. Target Behavior

### 5.1 Read-only proposal generation

```bash
scripts/bin/harness-cli propose
```

The command only displays active suggestions. It does not create backlog items,
change statuses, close work, or delete evidence.

Each suggestion has a stable internal `proposal_key`. The key is generated and
managed by Harness; users do not need to maintain it manually.

### 5.2 Explicit acceptance of one suggestion

```bash
scripts/bin/harness-cli propose --commit <proposal-key>
```

This command accepts exactly one identified suggestion.

It creates one backlog item with:

- the proposal key;
- status `open`;
- an accepted outcome or decision marker;
- the source proposal context needed for later explanation.

It does not commit every suggestion shown by `propose`, and it does not use a
list position as the identifier.

### 5.3 Idempotent acceptance

If an open backlog item already has the same proposal key, `--commit` returns
that existing item and creates no duplicate.

If a matching item is closed and there is no new evidence after its closure,
`--commit` creates nothing because the old issue has already been handled.

If a matching item is closed and new matching evidence exists after closure,
`propose` shows a regression suggestion. A human must explicitly commit that
suggestion, which creates a new backlog item linked to the old one through
`regression_of`.

The old closed item is never reopened or overwritten.

### 5.4 Conservative matching

Matching must use the same explicit proposal pattern or key. Similar wording,
the same topic, or a merely related friction is not enough to suppress or link
items automatically.

This prevents an unrelated improvement from disappearing because it happens to
use similar language.

### 5.5 Suppressed evidence remains explainable

Normal output shows active suggestions only.

```bash
scripts/bin/harness-cli propose --show-suppressed
```

This optional view explains why a suggestion is hidden, for example:

```text
Suppressed: backlog #11 was implemented by US-073.
No matching evidence was recorded after closure.
```

The explanation is derived from durable records. It does not require deleting
old traces, frictions, or interventions.

## 6. Story-to-Backlog Relationship

Stories may declare whether they resolve a backlog item or merely reference it.

```bash
scripts/bin/harness-cli story add \
  --id US-073 \
  --resolves-backlog 12 \
  --references-backlog 3
```

The same options apply to `story update`.

Relationship meanings:

| Relationship | Meaning | Verification effect |
| --- | --- | --- |
| `resolves` | The story claims to fix the backlog item. | A passing story verification may close it. |
| `references` | The story is related context only. | It never closes the backlog item automatically. |

Rules:

- The referenced backlog id must exist.
- A story/backlog pair cannot be both `resolves` and `references`.
- Existing links remain stable unless `--replace-backlog-links` is supplied.
- `--replace-backlog-links` replaces all links for that story with exactly the
  provided set.
- Adding a new `resolves` link to an already verified or implemented story
  requires a fresh `story verify`.
- Removing a link later does not reopen a backlog item that was already closed.

## 7. Verification And Closure

Only these commands may close a resolved backlog item automatically:

```bash
scripts/bin/harness-cli story verify <story-id>
scripts/bin/harness-cli story verify-all
```

### Passing verification

When a story passes verification, every backlog item linked with `resolves`
is closed as `implemented`.

The closure records deterministic outcome text, for example:

```text
Fixed by US-073; story verify passed at <timestamp>.
```

If the story resolves multiple backlog items, each one is closed independently.

If an already resolved backlog item is already closed, it remains unchanged.

### Failing or unavailable verification

If verification fails, or if the story has no usable verify command, no resolved
backlog item is closed.

Verification does not change `story.status`. A story can therefore be verified
without Harness silently moving it between planned, in-progress, or implemented
states.

### Later failure after closure

Once a backlog item is closed, a later failed verification does not reopen or
rewrite it. The closure records what was true at that time.

If new matching evidence appears after closure, the next `propose` run can show
a regression suggestion. A human decides whether to create the new regression
backlog item.

## 8. Controlled Cleanup And `--apply`

There is no broad mutation mode.

Apply actions must be named and narrowly scoped:

```bash
scripts/bin/harness-cli propose --apply <action>
scripts/bin/harness-cli propose --apply <action> --dry-run
```

`--dry-run` previews the exact changes and writes nothing.

The first permitted apply actions are metadata cleanup actions such as:

```bash
scripts/bin/harness-cli propose --apply backfill-keys
scripts/bin/harness-cli propose --apply reject-duplicates
```

`reject-duplicates` keeps the oldest open backlog item as canonical and rejects
newer duplicate items with an outcome such as:

```text
Duplicate of backlog #<canonical-id>
```

Apply actions may update backlog metadata and status, but they do not:

- delete traces;
- delete frictions;
- delete interventions;
- rewrite story packets;
- rewrite product documentation;
- close work as implemented; or
- replace historical evidence.

When an apply action actually changes rows, Harness records an operational
trace. If it changes nothing, it records no mutation trace.

## 9. Backward Compatibility And Migration

Existing backlog items may not have a proposal key.

Harness should backfill a key lazily when an old item is touched. Manual
`backlog add` remains valid without a proposal key.

When closing an old item, `backlog close` should attempt to backfill its key and
warn if the key cannot be derived. The close operation must not invent an
ambiguous relationship merely to avoid the warning.

Old traces, frictions, interventions, and closed backlog records remain
immutable history.

## 10. Proposed Data Model

Add structured fields rather than storing lifecycle relationships in free-form
notes.

### Backlog fields

```text
backlog.proposal_key       nullable, stable proposal identity
backlog.regression_of      nullable, prior backlog id
```

### Story relationship table

```text
story_backlog_link(
  story_id,
  backlog_id,
  relationship  -- resolves | references
)
```

The pair `(story_id, backlog_id)` should be unique. The relationship must be
validated against the allowed values and conflict rules above.

## 11. Edge Cases To Test Explicitly

| Scenario | Expected result |
| --- | --- |
| `propose` is run twice without changes | Same active suggestion; no writes. |
| Same proposal committed twice while open | One backlog item; second command returns the existing id. |
| Same key exists only on a closed item | No new item unless post-closure evidence exists. |
| New evidence appears after closure | Regression suggestion; no automatic backlog creation. |
| Similar but not identical proposal appears | It remains separate unless the explicit key/pattern matches. |
| Rejected proposal with no new evidence | Suppressed. |
| Rejected proposal with new matching evidence | Needs human review; no automatic backlog. |
| Duplicate cleanup in dry-run mode | Preview only; database unchanged. |
| Duplicate cleanup changes rows | Canonical item retained, duplicates rejected, one trace recorded. |
| Story references a missing backlog id | Command fails; no partial link is written. |
| Story has both relationship types for one backlog | Command fails; no partial link is written. |
| Passing story resolves an open backlog | Backlog closes as implemented. |
| Passing story references an open backlog | Backlog remains open. |
| Failing story resolves an open backlog | Backlog remains open. |
| Story has no verify command | Nothing closes. |
| One story resolves multiple items | Each resolved item closes independently. |
| One item is already closed | It remains unchanged. |
| Link is added after prior verification | Fresh verification is required before closure. |
| Link is removed after closure | Closed backlog remains closed. |
| Later verification fails after closure | Closed item remains closed; future evidence may propose regression. |
| Fresh database rebuild from changesets | Fields, links, and closure behavior survive rebuild. |
| Installer used on a fresh checkout | Schema and CLI behavior are available after install. |

## 12. Scope

### In scope

- Rust CLI behavior for proposal lifecycle and named apply actions.
- Backlog proposal identity and regression fields.
- Story-to-backlog relationship storage and validation.
- Verification-driven closure.
- Suppressed-proposal explanations.
- CLI help and repository documentation.
- Unit, integration, rebuild, and installer propagation tests.

### Out of scope

- Symphony Web UI changes.
- Automatic creation of regression backlog items.
- Automatic changes to `story.status`.
- Deletion of historical traces, frictions, interventions, or stories.
- Broad or unscoped `--apply` behavior.
- Reopening a closed backlog item after later failure.
- Starting a Symphony run as part of intake or review.
- Release tagging; the existing post-merge release workflow remains separate.

## 13. Validation Plan

### Code and schema checks

```bash
cargo fmt --check
cargo test --workspace
cargo clippy --workspace -- -D warnings
git diff --check
```

### CLI behavior checks

Exercise the full lifecycle in a temporary Harness database:

1. Run `propose` twice and prove it is read-only and stable.
2. Commit one proposal key and prove exactly one accepted backlog item exists.
3. Commit it again and prove no duplicate is created.
4. Add a story with `resolves` and `references` links.
5. Pass `story verify` and prove only the `resolves` item closes.
6. Fail verification and prove no open item closes.
7. Add post-closure evidence and prove `propose` shows a regression suggestion.
8. Prove `--show-suppressed` explains handled evidence.
9. Run named apply actions with and without `--dry-run`.
10. Prove historical traces, frictions, and interventions remain unchanged.

### Durable-state checks

```bash
scripts/validate-changeset-rebuild.sh
```

The rebuild must preserve proposal keys, regression links, story links, status
outcomes, and verification-driven closure behavior.

### Installer check

Install into a fresh temporary checkout or database and prove the new schema,
CLI options, and lifecycle behavior are present after installation. This is
required because installer propagation is part of the story contract.

## 14. Original Proposed Story Metadata (Superseded)

| Field | Proposed value |
| --- | --- |
| Story id | `US-073` |
| Title | Proposal-To-Backlog Lifecycle |
| Lane | `normal` |
| Intake type | `harness_improvement` |
| Primary surface | Harness CLI and durable state |
| Symphony execution | Not started by this review |
| Story status at creation | `planned` |

## 15. Resolved Review Decisions

1. The single `US-073 Proposal-To-Backlog Lifecycle` boundary was too large. It
   became epic E09 with dependency-ordered stories `US-073` through `US-080`.
2. Legacy key backfill is isolated in `US-080`; automatic duplicate rejection is
   out of scope.
3. `resolves` and `references` remain separate, with one designated resolver,
   and are implemented by `US-076`.
4. Ordinary verification does not close work. `US-077` adds explicit completion,
   fresh proof, implemented story status, and atomic accepted-backlog closure.
5. New covered evidence never creates work. New post-implementation or
   post-rejection evidence becomes a human-gated regression or reconsideration
   candidate in `US-078`.
6. Historical traces, decisions, relationships, closures, and outcome
   observations remain immutable evidence.
7. Each E09 story has its own proof plan, with high-risk stories split into
   overview, design, execution, and validation packets plus rebuild/installer
   evidence where relevant.

## 16. Approval Outcome

The direction was approved on 2026-07-10 with one material correction: backlog
closure must use explicit story completion with fresh proof rather than being a
side effect of ordinary verification.

The work is now governed by:

- `docs/decisions/0008-self-improving-harness-lifecycle.md`
- `docs/stories/epics/E09-self-improving-harness-lifecycle/README.md`
- the dependency-ordered E09 story packets `US-073` through `US-080`

Do not create the former single-story packet named in the original draft. This
review record is non-normative historical evidence.
