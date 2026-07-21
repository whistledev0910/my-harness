# Reduction Phase 4 — Control-Plane Freeze

## Status

Complete on 2026-07-21. Decisions 0019–0021 removed SQLite lifecycle operations
from the default workflow and installation. Decision 0022 and the Phase 4
native-artifact boundary now freeze accidental upstream lifecycle writes while
preserving readable history and protocol-v1 compatibility.

The previous Phase 4 mechanical-verification roadmap is preserved at
`docs/compatibility/phase-4-mechanical-verification-legacy.md`. It describes the
superseded database-centered phase sequence and is not current authority.

## Anchor

OpenAI's
[Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)
optimizes for agent-legible repositories, direct development and application
tools, mechanically enforced invariants, observable validation, and minimal
human attention. Manual lifecycle records are not a substitute for those
capabilities.

Repository Harness therefore uses Git-native product, design, plan, decision,
code, test, CI, and runtime evidence as current authority. The SQLite control
plane remains a compatibility surface, not an alternative current roadmap.

## Target Outcome

Reach a state where:

```text
new upstream work
  -> writes only current Git-native authority and product evidence

existing SQLite state
  -> remains readable and reproducible as compatibility history

external orchestration
  -> keeps its published contract until a tested migration exists

obsolete lifecycle writes
  -> warn, require explicit compatibility intent, then freeze in stages
```

The phase does not succeed merely because documentation calls the database
legacy. New upstream lifecycle writes must become observable, current authority
must be complete without them, and external consumers must have a recoverable
path before rejection or deletion.

## Current State Inventory

The upstream ignored database was inspected read-only at Phase 4 start:

| Surface | Current legacy state | Authority disposition |
| --- | ---: | --- |
| Nonterminal stories | 3 | Preserved history; absent from the current active-plan index. |
| Open backlog items | 5 | Preserved history; not the current roadmap. |
| Intakes | 133 | Historical compatibility records. |
| Traces | 178 | Historical compatibility records, not completion proof. |
| Interventions | 16 | Historical compatibility records. |
| Current/proposed decision rows | 15 | Readable history; current decisions are indexed Git documents. |

The three nonterminal stories are US-086 through US-088 from the superseded
self-improvement roadmap. Their `planned` values remain historical facts. Phase
4 does not mark them implemented, rejected, or retired merely to make SQLite
match the new authority model.

Validation also exposed a useful boundary example: the ignored local database
has 133 intake rows, while a fresh replay of tracked state has 134 and includes
intake 224. Phase 4 does not silently repair that local compatibility copy.
Tracked replay remains reproducible, and the mismatch is reported as local
materialization drift rather than treated as a roadmap disagreement.

## Evidence Matrix

| Gate | Required evidence | Starting state | Status |
| --- | --- | --- | --- |
| P4-01 Authority boundary | Current workflow, plan, and decision indexes identify Git-native authority without database queries. | Decisions 0019–0021 and core profile already establish this. | Passed before Phase 4 |
| P4-02 Legacy inventory | Nonterminal and open SQLite state is read without mutation and receives an explicit disposition. | Counts and identities captured in the active plan and this phase. | Passed |
| P4-03 Warning runway | Human lifecycle mutation against upstream default state prints an actionable compatibility warning but still behaves normally. | Focused Rust tests cover source/default, query, isolated-database, and machine boundaries. | Passed |
| P4-04 Machine compatibility | Protocol JSON, exit codes, capabilities, and stored mutation behavior remain unchanged during the warning stage. | All 50 public command paths and the protocol-v1 native artifact smoke remain unchanged. | Passed |
| P4-05 Explicit compatibility intent | Later legacy writes require a deliberate compatibility selection rather than occurring accidentally. | Source-default human lifecycle writes require global `--compatibility-write`; intent is visible in argv and stderr. | Passed |
| P4-06 Current-state export | Any genuinely current authority that exists only in SQLite is moved read-old/write-new into Git-native surfaces. | Direct row/index comparison found no current SQLite-only authority; every active-looking row has a historical disposition. | Passed; no export required |
| P4-07 Write freeze | Obsolete lifecycle writes are rejected without preventing history reads or required orchestration. | Native-artifact proof rejects accidental writes before mutation and preserves JSON, explicit DB, consumer, read, and maintenance paths. | Passed |
| P4-08 Deletion boundary | Code/schema removal has direct usage evidence, migration proof, and recovery. | Inventory confirms protocol-v1, CLI-profile, reconstruction, and recovery consumers still exist; implementation is explicitly retained. | Passed by retention decision |

## First Slice

The first slice is a deliberately non-destructive warning runway:

1. Preserve the old root Phase 4 as compatibility history.
2. Publish decision 0022 and one active execution plan.
3. Classify CLI operations without removing a public command.
4. Warn only for human-oriented lifecycle mutations against this source
   repository's default database.
5. Keep machine JSON operations, isolated databases, installed consumers,
   read-only queries, bootstrap/migration, snapshot, replay, and rebuild quiet
   and behaviorally unchanged.
6. Prove public command and protocol compatibility mechanically.

Concrete cause and effect:

```text
maintainer accidentally runs `harness-cli intake ...` in repository-harness
  -> command still records the row during the runway
  -> stderr explains that new upstream authority belongs in Git-native plans
  -> the accidental extension of legacy state is visible

Symphony invokes `story update --json ...`
  -> no warning contaminates machine interaction
  -> response envelope and mutation semantics remain protocol v1
```

## Final Freeze

After the warning runway and direct consumer inventory:

```text
maintainer runs `harness-cli intake ...` against the source default database
  -> command exits before opening the write transaction
  -> no row or semantic changeset is created
  -> remediation points to Git-native authority

maintainer runs `harness-cli --compatibility-write intake ...`
  -> stderr records the explicit compatibility selection
  -> existing mutation and semantic capture execute normally

protocol, installed consumer, or explicit HARNESS_DB_PATH operation
  -> no new flag required
  -> published behavior remains unchanged
```

The exact legacy-row and consumer dispositions are recorded in
`docs/compatibility/phase-4-write-consumer-inventory.md`.

## Stop Conditions

The freeze evaluated these stop conditions before advancing:

- a supported consumer still requires the write and has no migration;
- current authority exists only in the database;
- read-old/write-new export cannot be reproduced;
- rejection would change protocol v1 without a versioned decision; or
- rollback depends on editing or deleting historical rows.

## Phase Exit

Phase 4 completes only when new upstream lifecycle writes are frozen, all
current authority is repository-native, old state remains readable, and every
supported external mutation has either a retained versioned home or a tested
migration. Implementation deletion is a later decision unless the same evidence
also proves it safe.

Those conditions are met: accidental source-default human writes are frozen,
the authority audit found no current SQLite-only work, tracked state remains
replayable, and protocol-v1 plus explicit compatibility consumers retain their
tested homes. The implementation remains because the deletion audit proved it
is still used, not because deletion was left unexamined.
