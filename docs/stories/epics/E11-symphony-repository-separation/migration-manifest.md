# E11 Preliminary Migration Manifest

This is the discovery-time ownership map. `US-089` must turn it into an exact,
machine-checked manifest before any history filtering or deletion.

## Frozen Discovery Snapshot

| Item | Observed state |
| --- | --- |
| Source | clean `repository-harness/develop@6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9` |
| Source divergence | `develop` is 18 commits ahead of `main`; latest Harness lifecycle work exists only on `develop` |
| Target | empty local clone with unborn `main` |
| Target remote | `git@github.com:hoangnb24/symphony.git`; no heads or tags returned |
| Symphony source | 47 tracked files, 14 Rust files, 9,219 Rust LOC, 99 Rust tests, 19 Playwright tests |
| Symphony lineage | scope begins at `e7a124b`; runner source begins at `444d793`; 34 commits touch the crate |
| Live local Harness DB | 84 stories before E11 registration; 189 intakes after intake `#193`; 238 traces; 16 backlog rows; 4 decisions |
| Clearly Symphony-owned live rows | 41 stories (`US-032` through `US-071` plus `US-SYM-001`); `US-028`-`US-031` are core prerequisites and `US-072` is mixed/core. A broad ID/text scan found 87 candidate intakes and 109 candidate traces that still require operation-level ownership classification. |
| Tracked semantic history at discovery | 31 changeset files: 13 Symphony-owned, 15 Harness-core-owned, 3 mixed; E11 planning later adds one transitional core changeset |
| Rebuild behavior | 59 stories rebuilt; core `US-001`–`US-025` and planned `US-086`–`US-088` are not reconstructed |
| Local ignored runtime | about 8.8 GB under `.symphony` with 15 worktrees; about 33 MB under `.harness/runs` |

After durable E11 planning registration, the live DB has 16 discovered user
tables and these concrete row counts (discovery evidence only; `US-089` must
repeat the export at its frozen cutoff):

| Table | Rows |
| --- | ---: |
| `audit_evidence_episode` | 0 |
| `backlog` | 16 |
| `backlog_outcome_observation` | 0 |
| `changeset_applied` | 30 |
| `decision` | 5 |
| `intake` | 190 |
| `intervention` | 13 |
| `legacy_evidence_snapshot` | 4 |
| `proposal_evidence_link` | 9 |
| `schema_version` | 12 |
| `story` | 96 |
| `story_backlog_link` | 0 |
| `story_dependency` | 29 |
| `story_hierarchy` | 0 |
| `tool` | 5 |
| `trace` | 251 |

The pre-plan counts remain relevant for causality: E11 added 12 story rows, 14
final dependency edges, one replayable intake, one decision, 12 planning
traces, two reviewer-correction interventions, and one final correction trace.
That correction evidence is audit history, not implementation proof.

The live/rebuild mismatch means neither `harness.db` nor the committed
changesets may be treated as a complete, portable source of truth by itself.
All 15 registered worktrees were observed dirty because their generated
`AGENTS.md` differs. Worktree
`run_1783159027653025000_6614_0` also contains a real roughly 380-line
uncommitted code/UI diff, so bulk deletion would cause actual source loss.
The Git bundle protects committed refs only. `US-089` must separately capture
binary-safe staged/unstaged patches, untracked archives, HEADs, and hashes for
every dirty worktree and rehearse their restoration.

## Path Ownership Actions

### Move With Filtered History To Symphony

- `crates/harness-symphony/**`
- `docs/SYMPHONY_SCOPE.md`
- `docs/SYMPHONY_QUICKSTART.md`
- `docs/product/symphony-web-ui-controller.md`
- `docs/stories/US-046-first-class-symphony-codex-adapter.md`
- `docs/stories/epics/E05-symphony-local-runner/**`
- `docs/stories/epics/E06-symphony-review-sync/**`
- `docs/stories/epics/E07-symphony-automation/**`
- `docs/stories/epics/E08-symphony-web-ui-controller/**`
- Symphony-specific review evidence selected by `US-089`

The filtered target may retain these source paths initially. Documentation can
be reorganized in a normal target commit after the filter commit-map is saved.

### Retain As Generic Harness Core

- `crates/harness-cli/**`
- `scripts/schema/**`
- `scripts/install-harness.sh`, `scripts/install-harness.ps1`
- `scripts/build-harness-cli-release.sh`
- Generic Harness policy, templates, decisions, and phase docs
- Generic Harness stories `E01`–`E03`, `E09`, and `E10`
- `HARNESS_REPO_ROOT` and `HARNESS_DB_PATH` resolution
- `HARNESS_RUN_ID` semantic operation logging
- Changeset header/version, apply, idempotency, and rebuild behavior
- Story dependency storage, cycle-safe mutation/query, and replay
- Story hierarchy storage; `US-092` must make its public query/mutation
  ownership explicit instead of leaving it as a Symphony-only raw table
- Explicit story completion and atomic resolver closure
- Validation child-process quarantine for `HARNESS_RUN_ID`,
  `HARNESS_RUN_MODE`, and `HARNESS_DB_PATH`

These capabilities were motivated or exercised by Symphony, but they are
general repository-workflow capabilities. Removing them would break the
Harness CLI rather than separate products.

### Rewrite In Repository-Harness

- Root `Cargo.toml` and `Cargo.lock`
- `README.md`
- `docs/README.md`
- `docs/product/README.md`
- `docs/stories/epics/README.md`
- `.gitignore`
- `.github/workflows/harness-cli-release.yml`
- `.github/workflows/post-merge-maintenance.yml`
- `scripts/harness-install-files.txt`
- `scripts/validate-changeset-rebuild.sh`
- `scripts/test-validate-changeset-rebuild.sh`
- `scripts/schema/007-story-dependencies.sql` comments
- `scripts/schema/008-story-hierarchy.sql` comments and public ownership
- Active Symphony wording and verify commands in mixed E09/E10 stories,
  `US-072`, `US-081`, improvement docs, and reviews

Concrete existing defects this rewrite must close:

1. The installer copies root and product README files containing Symphony links
   but does not copy the linked Symphony docs or source.
2. CLI release CI runs `cargo test --workspace`, so Symphony's 99 tests gate a
   Harness CLI release.
3. Post-merge treats root Cargo metadata changes as CLI changes, so a Symphony
   dependency update can bump the Harness CLI.
4. The rebuild validator hard-codes Symphony story IDs and calls them proof of
   generic replay correctness.
5. The installed `.gitignore` includes UI, Electron, and `.symphony` entries
   that are not part of the generic template contract.

### Do Not Migrate As Product Source

- `harness.db`, `harness.db-wal`, `harness.db-shm`
- `.symphony/**`
- `.harness/runs/**`
- `target/**`, `dist/**`, `node_modules/**`, Web build/test output
- `.agents/skills/impeccable/**`
- `.codex/hooks.json`
- `.impeccable/config.local.json`
- The combined monorepo `Cargo.lock`

`.agents` and the Codex hook are UI-development tooling, not Symphony runtime
source. Symphony may document an optional external design provider; it must run
cleanly when that provider is absent.

### Archive Or Repackage, Do Not Keep Active In Harness

- `.codex/skills/harness-intake-griller/**`: preserve provenance, but remove its
  active project-local installation. If retained for Symphony, package it as an
  independently installable extension rather than a hidden Harness-core tree.
- Historical Symphony changelog and review evidence: preserve in Git history,
  the target history, or an explicit archive.
- Existing tracked `.harness/changesets`: preserve through source history,
  bundles, and backups, but remove the repository's live files from active core
  replay and tests. Retain the generic installer/ignore rule that permits a
  consuming Harness repository to commit its own changesets.

## Changeset Partition

### Exact Discovery-Time Ownership

Symphony-owned:

- `run_0000000002_retire_stale_symphony_docs.changeset.jsonl`
- `run_1782473523_99206.changeset.jsonl`
- `run_1782536604_52965.changeset.jsonl`
- `run_1782543459_701.changeset.jsonl`
- `run_1782550121_26667.changeset.jsonl`
- `run_1783164291664744000_6614_2.changeset.jsonl`
- `run_1783178537862657000_95182_0.changeset.jsonl`
- `run_1783179886029971000_7111_0.changeset.jsonl`
- `run_1783224245101133000_18033_0.changeset.jsonl`
- `run_1783399293702861000_us069.changeset.jsonl`
- `run_1783405248236036000_24617_0.changeset.jsonl`
- `run_1783523200000000000_us071.changeset.jsonl`
- `run_1783530000000000000_impeccable_tool.changeset.jsonl`

Harness-core-owned:

- `run_1783670632_e09_planning.changeset.jsonl`
- `run_1783676834844503000_28702_0.changeset.jsonl`
- `run_1783680342594999000_45616_0.changeset.jsonl`
- `run_1783682363_us075_selective_proposal_decision.changeset.jsonl`
- `run_1783685000000000000_us076_story_backlog_relationships.changeset.jsonl`
- `run_1783692800000000000_us081_validation_subprocess_quarantine.changeset.jsonl`
- `run_1783698675355923000_95563_0.changeset.jsonl`
- `run_1783699620299211000_2829_0.changeset.jsonl`
- `run_1783700451018024000_10445_0.changeset.jsonl`
- `run_1783702000000000000_us077_completion_closure.changeset.jsonl`
- `run_1783741281_us082_review_finding_closure.changeset.jsonl`
- `run_1783741400_e09_proof_parity.changeset.jsonl`
- `run_1783743300_us083_post_review_closure.changeset.jsonl`
- `run_1783744000_us084_proof_audit_closure.changeset.jsonl`
- `run_1783745900_us085_semantic_integrity.changeset.jsonl`

Mixed:

- `run_0000000000_seed_symphony_index.changeset.jsonl`
- `run_1783163412740491000_6614_1.changeset.jsonl`
- `run_1783610000000000000_us072.changeset.jsonl`

Post-discovery transitional core planning:

- `run_1783785600_e11_symphony_repository_separation_planning.changeset.jsonl`
  records decision `0009`, `US-089` through `US-100`, and their dependency
  edges. `US-097` must archive it before repository-harness stops tracking live
  operation logs.

This 32-file set is the frozen planning baseline, not the final partition
cutoff. `US-097` must create a second manifest covering every then-present file,
including `US-092` protocol work and `US-093` proxy/receipt operations, hash and
classify the delta, and archive both manifests.

The three mixed files require operation-level handling, not whole-file moves:

| Changeset | Why mixed | Required treatment |
| --- | --- | --- |
| `run_0000000000_seed_symphony_index.changeset.jsonl` | Seeds Symphony stories and also establishes historical operational state | Preserve in the provenance bundle; create ownership-specific exports rather than replay it into clean core state. |
| `run_1783163412740491000_6614_1.changeset.jsonl` | Implements `US-065` and adds core backlog item `#13` | Export the Symphony story evidence and core backlog evidence separately. |
| `run_1783610000000000000_us072.changeset.jsonl` | Combines core audit/provider cleanup with Symphony story verification and UI providers | Retain synthetic core proof for provider behavior; move Symphony proof/provider ownership to the target context. |

The 13 Symphony-owned and 15 core-owned files must be enumerated by exact path
in the final `US-089` manifest. No implementation may infer ownership only from
filename or story-number ranges.

## Durable State Actions

The final inventory is table-driven, not limited to this summary. `US-089` and
`US-097` discover every non-internal user table through `sqlite_master`, classify
every row/edge, and prove foreign-key closure plus per-table count/stable-UID
sets. Known tables that must not be skipped include `intervention`,
`story_backlog_link`, `proposal_evidence_link`, `audit_evidence_episode`,
`backlog_outcome_observation`, `legacy_evidence_snapshot`,
`changeset_applied`, and `schema_version`. Epoch/derived rows are reset or
recomputed rather than copied blindly.

| Record | Repository-harness action | Symphony action |
| --- | --- | --- |
| Implemented Symphony stories/traces | Preserve in backup/history; remove from active core DB | Keep historical docs/provenance, not an automatically runnable queue |
| Proposed Symphony backlog `#10`, `#12`, `#14` and other confirmed product work | Remove from core after export | Re-intake deliberately in target if still wanted |
| Symphony UI tool providers | Remove from core registry | Register only in a Symphony development Harness and only when installed |
| Core E09/E10 stories and backlog | Preserve/reseed as active core state | Do not import |
| E11 separation stories | Preserve source-owned work plus completed/`changed` non-runnable target receipt proxies and all original edges until completion | Own runnable `US-093`-`US-096`; emit checksummed completion receipts, never duplicate runnable ownership |
| Raw database | Back up outside Git, checksum, then replace with core-owned local state | Do not copy blindly; preserve the target DB initialized by `US-093` and add reviewed work through its CLI |

If `US-097` activates before target `US-096` completes, the fresh core DB must
retain the `changed` US-096 source proxy and its edges to US-098/US-100. The
receipt verifier and normal verified completion later unblock those source
stories; partition never treats the proxy as disposable Symphony backlog.

## Historical Reference Allowlist After Cutover

Symphony may remain named in:

- decision `0009`;
- completed E11 separation packets and validation evidence;
- dated `CHANGELOG.md` entries and merged PR metadata;
- an explicit archive or provenance note;
- a short historical note explaining that Symphony was the first consumer of
  retained generic capabilities.

It must not remain active in:

- Harness README commands or installation guidance;
- current product docs or active epic sequence;
- story verification commands;
- registered core tool providers;
- rebuild fixture expected IDs;
- core CI package selection;
- installer payload links or installed ignore rules;
- active core matrix, backlog, audit findings, proposals, or changesets.

## Green Baseline Evidence

The following passed against the frozen discovery checkout:

```text
cargo test --workspace
  harness-cli: 73 passed
  harness-symphony: 99 passed

npm --prefix crates/harness-symphony/web-ui run build
  passed; 1,594 modules transformed

npm --prefix crates/harness-symphony/web-ui run e2e
  19 passed

npm --prefix crates/harness-symphony/web-ui run desktop:smoke
  passed

cargo fmt --check
cargo clippy --workspace -- -D warnings
scripts/validate-changeset-rebuild.sh
  all passed
```

This evidence is a comparison baseline, not proof that extraction has already
succeeded.
