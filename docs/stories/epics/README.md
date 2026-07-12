# Epic Story Packets

Create epic folders here only when work begins or when product decisions need a
durable home.

Suggested naming:

```text
E01-domain-name/
E02-domain-name/
E03-domain-name/
```

Create the real epic names from the user-provided spec, not from this template.

## Active Epic Sequence

| Epic | Theme | Exit Signal |
| --- | --- | --- |
| `E04-symphony-cli-prerequisites` | Make `harness-cli` support copied DBs, semantic changesets, replay, and rebuild. | `harness.db` is a rebuildable local index over committed changesets. |
| `E05-symphony-local-runner` | Build the on-demand local workbench: doctor, work list, isolated prepare, run contract, result validation, and status. | `harness-symphony run <story-id> --prepare-only` satisfies the MVP acceptance criteria. |
| `E06-symphony-review-sync` | Make run artifacts reviewable and merged changesets syncable. | PR artifacts are reviewable and `sync` is idempotent. |
| `E07-symphony-automation` | Add lightweight tiny runs and later unattended automation. | Automation reuses the proven local run contract and sync model. |
| `E08-symphony-web-ui-controller` | Expose Harness stories and Symphony runs through the local browser and Electron controller. | Humans can start, observe, review, recover, merge-gate, and sync dependency-aware work from the controller. |
| `E09-self-improving-harness-lifecycle` | Carry evidence-backed Harness proposals through acceptance, verified closure, recurrence, and measured outcome. | Handled evidence stays explainable and suppressed; only new recurrence becomes human-reviewable work. |
| `E10-harness-signal-quality` | Retire obsolete or synthetic improvement signals and expose multidimensional Harness health. | Current signal quality and lane-aware trace health are visible without deleting history. |
| `E11-symphony-repository-separation` | Move Symphony into its own product repository and restore repository-harness as a reusable template. | Standalone Symphony passes against a released Harness contract, and repository-harness contains only core source, docs, tooling, and active durable work, with allowlisted completed migration evidence. |
