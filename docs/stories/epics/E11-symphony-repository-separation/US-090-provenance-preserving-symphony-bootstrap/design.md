# Design

## Domain Model

The import has three immutable anchors:

- source commit SHA;
- selected path manifest SHA;
- filter old-to-new commit map SHA.

Together they answer which original content produced any target commit.

## Application Flow

```text
verified source bundle
  -> disposable clone
  -> create one extraction branch at frozen SHA and remove/exclude other refs
  -> checksum-verified pinned git-filter-repo
  -> multi-path filter
  -> verify exclusions and representative lineage
  -> add target provenance note
  -> tag raw import
  -> push filtered HEAD:main plus raw-import tag only
```

## Interface Contract

The target provenance note records:

- source repository URL and SHA;
- extraction date and tool version;
- manifest checksum;
- filter command;
- commit-map location/checksum;
- source recovery tag/bundle checksum;
- paths intentionally excluded.
- pinned filter-repo package/source URL and verified checksum;
- exact two refspecs authorized for the first push.

## Data Model

Existing `.harness/changesets` are excluded from the filtered target worktree
and active history selection. They remain preserved in the verified source
bundle/raw archive; ownership-specific active state is created through the
target CLI by `US-093` and reconciled by `US-097` with new identities.

## UI / Platform Impact

None yet. Existing source paths stay intact.

## Observability

The import report records source and target commit counts, selected path counts,
excluded forbidden paths, and representative `git log --follow` output.

## Alternatives Considered

1. Snapshot initial commit. Rejected because the target is empty and can still
   preserve useful history cheaply.
2. `git subtree split` on only `crates/harness-symphony`. Rejected because it
   drops product docs and distributed story history.
3. Filter the live source checkout. Rejected because a command mistake could
   rewrite the canonical repository.
