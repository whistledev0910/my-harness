# repository-harness

Turn any software repo into an agent-ready workspace.

`repository-harness` is a repository-level operating harness for Claude Code,
Codex, Cursor, and other coding agents. It gives agents the missing project
context they need before they change code: where to start, what the product
contract says, how risky the work is, what proof is required, and which
decisions future agents should inherit.

The app is what users touch. The harness is what agents touch.

## Why Star This Repo

Star this repo if you want practical, reusable patterns for making AI-assisted
software development more reliable, inspectable, and easier for humans to steer.

This project is exploring a simple idea:

> Coding agents do not only need better prompts. They need better repositories.

## The Problem

Most repos are built for humans reading code in a familiar codebase. Coding
agents usually enter with only a chat prompt and a shallow snapshot of files.
That leads to common failure modes:

- The agent edits code before understanding product intent.
- Important constraints live only in chat history or in someone's head.
- Validation expectations are vague or discovered too late.
- Architecture tradeoffs are repeated instead of inherited.
- Large requests do not get broken into reviewable story-sized work.

## The Harness Approach

A repository starts to have a harness when it helps an agent answer practical
engineering questions without relying only on chat history:

- What should I read first?
- What type of work is this?
- Which product contract does it affect?
- How risky is the change?
- What proof will show the work is done?
- What decision or lesson should future agents inherit?

In this repo, those answers live in:

- `AGENTS.md` — the stable agent shim with local project notes and Harness
  doc links.
- `docs/HARNESS.md` — the human-agent collaboration model.
- `docs/FEATURE_INTAKE.md` — tiny, normal, and high-risk work classification.
- `docs/ARCHITECTURE.md` — architecture discovery and boundary rules.
- `docs/TEST_MATRIX.md` — behavior-to-proof validation expectations.
- `docs/stories/` — story packets and backlog items.
- `docs/decisions/` — durable decisions and tradeoffs.
- `docs/templates/` — reusable spec, story, decision, and validation templates.

OpenAI describes this shift as an agent-first world where humans steer and
agents execute:

https://openai.com/index/harness-engineering/

## Install Harness Into A Project

The default installer is safe for existing repositories: it installs only
Harness documentation under `.harness/` and adds or refreshes a marked block in
`AGENTS.md`. It does not replace the project's `README.md`, `docs/`, `scripts/`,
or existing agent instructions.

Preview the change from the target project directory:

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --dry-run
```

Install it:

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --yes
```

Or target another existing directory:

```bash
curl -fsSL "https://raw.githubusercontent.com/whistledev0910/my-harness/main/scripts/install-harness.sh" | bash -s -- --directory /path/to/project --yes
```

Re-running the command updates vendored Harness docs and the marked `AGENTS.md`
block without duplicating it. The docs-only installer deliberately skips the
Rust CLI, SQLite database, dashboard, and helper scripts; projects keep using
their existing issue tracking, decisions, documentation, and validation tools.

Installed shape:

```text
existing-project/
  AGENTS.md                 # existing content preserved; one Harness block
  docs/                     # untouched project docs
  scripts/                  # untouched project scripts
  .harness/
    README.md               # docs-only precedence and path rules
    VERSION
    docs/                   # vendored Harness guidance
```

## Try The Flow

The fastest way to understand the harness is to inspect the tiny demo:

- `docs/demo/README.md`: shows how a simple product idea becomes product docs,
  stories, validation expectations, and decisions before implementation starts.

A typical flow looks like this:

```text
human intent or product spec
  -> product contract
  -> feature intake
  -> story packet
  -> validation expectations
  -> implementation work
  -> decision or lesson captured for future agents
```

Implementation prompts do not go straight to code. They first pass through
feature intake, become story-sized work when needed, and then carry both product
validation and harness maintenance expectations.

## Tool Registry

This section applies when working on the Harness source repository or when a
project separately installs the full CLI. Docs-only installations skip it.

The harness can use optional external tools (linters, code-graph servers,
deploy checks) without depending on any of them. You register a tool as a
provider of a *capability*, the harness scans whether it is actually present,
and a workflow step uses whatever is equipped — an absent tool is a clean skip,
never a failure.

```bash
# register a tool as a provider of a capability
scripts/bin/harness-cli tool register --name deploy-check --kind cli \
  --capability deploy-verification --command ./scripts/deploy-check.sh \
  --responsibility Verification --description "Verify deploy health before release"

# scan presence (writes present/missing/unknown)
scripts/bin/harness-cli tool check

# a step looks up what is equipped for a purpose
scripts/bin/harness-cli query tools --capability deploy-verification --status present
```

Kinds (`cli`, `binary`, `mcp`, `skill`, `http`) make it agent-generic: each
agent runtime uses what it can orchestrate. See `docs/TOOL_REGISTRY.md` for the
full model, the degrade ladder, and how to wire a tool into a flow step.

## Current State

This repository is in Harness v0.

There is no application implementation and no baked-in product specification
yet. The current work is the reusable project harness: the file structure,
agent operating model, feature intake process, story templates, and validation
expectations that help humans and agents turn a future user-provided spec into
implementation work.

## Product Sources

No product contract is currently defined.

When a user provides a project specification, add or reference it as the input
spec for the first buildout, then derive smaller living artifacts from it:

- `docs/product/`: current product contract files, created from the spec.
- `docs/stories/`: story packets and backlog created from selected work.
- `docs/TEST_MATRIX.md`: behavior-to-proof control panel.
- `docs/decisions/`: durable decisions and tradeoffs.

Do not keep a project-specific spec or product breakdown in this harness until
a real project supplies one.

## Repository Structure

```text
project/
  AGENTS.md
  README.md
  docs/
    HARNESS.md
    FEATURE_INTAKE.md
    ARCHITECTURE.md
    TEST_MATRIX.md
    HARNESS_BACKLOG.md
    product/
    stories/
    decisions/
    demo/
    templates/
  scripts/
    README.md
```

## Contributing

This project is early and benefits most from real-world agent failure cases,
example harness installs, docs improvements, and reusable workflow patterns.
See `CONTRIBUTING.md` for contribution ideas.

Useful contributions include:

- Show how the harness works in a real project.
- Add missing templates or improve existing ones.
- Propose validation patterns for different stacks.
- Share failures where an agent made the wrong change because the repo lacked
  context.
- Compare harness behavior across Claude Code, Codex, Cursor, and other tools.

## Share

If this idea resonates, please star the repo and share it with someone building
with coding agents.

Short description:

> An agent-ready repo harness for Claude Code, Codex, Cursor, and other coding
> agents: AGENTS.md, product contracts, story packets, validation matrix, and
> decision records.
