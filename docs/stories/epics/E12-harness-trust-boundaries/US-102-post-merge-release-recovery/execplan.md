# Exec Plan

## Goal

Recover the failed post-merge Harness CLI release without retagging `0.1.16`,
and make future tags contingent on platform proof.

## Scope

In scope:

- Frozen Bash and PowerShell compatibility checks for `0.1.14`.
- Old-to-candidate transition proof in pull-request and release workflows.
- Candidate-aware release identity with strict existing-tag checks.
- Proof-before-tag post-merge sequencing.
- Release-affecting path classification, workflow contracts, and docs.

Out of scope:

- CLI runtime or schema behavior changes.
- Destructive tag cleanup.
- Publishing before the correction is reviewed and merged.
- Changes to the stale mixed-ownership default Harness database.

## Risk Classification

Risk flags:

- Public contracts.
- Cross-platform release behavior.
- Existing tested behavior.
- Weak pre-merge transition proof.

Hard gates:

- Current validation requirements must not be weakened.
- Existing release tags must remain immutable.
- The source/tag/crate identity relationship must fail closed.

## Work Phases

1. Reproduce and localize the failed hosted run.
2. Record the compatibility and promotion boundary.
3. Add frozen historical smokes and transition fixtures.
4. Move tag creation behind the complete build matrix.
5. Add negative identity and workflow sequencing tests.
6. Run focused, pre-merge, and hosted-equivalent validation.
7. Record proof and prepare the monotonic patch-release recovery.

## Stop Conditions

Pause for human confirmation if:

- Recovery would require moving or deleting `harness-cli-v0.1.16`.
- The current candidate smoke would need to lose an assertion.
- An existing tag could be silently accepted at a different commit.
- The fix requires product-owned Symphony state or source.
