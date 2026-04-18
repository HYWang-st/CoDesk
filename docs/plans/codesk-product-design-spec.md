# CoDesk Product Design Spec — One-Command Shared Workspace + Dual-Agent Bootstrap

> **For the next implementing agent:** Read this document first, then inspect the current codebase. This spec supersedes earlier vague product assumptions. Treat this file as the source of truth for the next productization phase.

**Status:** Approved design target for the next iteration after MVP baseline `dea1b99`

**Repository:** `/Users/starsama/Code/CoDesk`

**Current baseline reality:** The repository already contains a file-first collaboration workspace model, record generators, validation, status summary, weekly digest rendering, and directional sync packet rendering. It does **not** yet implement a true one-command onboarding flow, a persistent workspace config, agent bootstrap prompt generation, or mainstream-agent default discovery.

---

## 1. Product goal

CoDesk should let a user set up a collaboration loop between two AI agents with **one command**.

The intended user experience is:

1. User runs a single CoDesk command.
2. CoDesk should prefer automatic defaults and environment discovery, and only ask for minimal setup information when it cannot infer a safe value.
3. CoDesk creates a shared workspace on disk.
4. CoDesk writes a durable workspace config describing the collaboration contract.
5. CoDesk prints **two copy-paste-ready prompts**:
   - one for Agent 1
   - one for Agent 2
6. The user pastes each prompt into the corresponding agent.
7. Each agent uses the shared workspace plus its own scheduling capability (for example cron-style scheduled tasks) to perform recurring sync.
8. Result: the two agents can keep progress aligned through a shared blackboard without requiring the user to manually orchestrate every sync.

### Non-goal for this phase

This phase does **not** need to implement a universal scheduler backend inside CoDesk. It is enough for CoDesk to:
- encode the sync policy in config
- generate prompts that instruct each agent how often to sync
- generate scheduler-ready guidance in the prompt text

In other words: **CoDesk does not need to own scheduling execution yet; it needs to bootstrap agents that can schedule themselves.**

---

## 2. The exact target user experience

### 2.1 Primary flow

The user should be able to run something conceptually like:

```bash
codesk setup
```

or:

```bash
PYTHONPATH=src python3 -m codesk.cli setup
```

This command should:

1. Automatically choose or discover sensible defaults for:
   - shared workspace parent directory
   - agent identities for mainstream agents
   - mainstream agent installation / working directories when known
   - sync frequency when the user does not care
2. Ask for or accept only the remaining values that cannot be inferred safely, such as:
   - collaboration / project name
   - collaboration objective
   - user notes or collaboration preferences
3. Create the shared workspace.
4. Create a durable config file under that workspace.
5. Optionally seed an initial project record.
6. Print a concise summary of what was created.
7. Print two clearly delimited prompt blocks ready for copy/paste.

### 2.2 Expected command-line output shape

The final CLI output should resemble this structure:

```text
CoDesk workspace created at:
/absolute/path/to/.../assistant-sync

Config written to:
/absolute/path/to/.../assistant-sync/config.yaml

Next step:
1. Copy PROMPT A into Agent 1
2. Copy PROMPT B into Agent 2
3. Ask each agent to confirm its first sync run

===== PROMPT FOR AGENT 1 =====
...

===== PROMPT FOR AGENT 2 =====
...
```

This output format matters. The next agent should optimize for **low-friction copy/paste onboarding**.

### 2.3 Default-first behavior is a product requirement

This product should feel close to zero-config for common cases.

The preferred behavior is:

1. Default-create a shared sync workspace without forcing the user to design the folder layout manually.
2. Preload mainstream agent names by default.
3. Auto-discover mainstream agent home / install / workspace paths when these defaults are well known on the current platform.
4. Only prompt the user when discovery fails, multiple plausible paths exist, or the user explicitly wants custom values.

For the current phase, the first built-in mainstream pair should be:
- `hermes`
- `openclaw`

The design must keep an extension point for future agents.

---

## 2A. Default assumptions for mainstream agents

The setup flow should support a default-first experience for popular agents.

### 2A.1 Built-in agent registry concept

The next implementation should introduce a lightweight built-in registry of known agents.

The registry should be able to describe, per agent:
- canonical name
- display name
- likely home / install / working directories by platform
- any prompt-generation hints specific to that agent
- whether the agent is known to support scheduled tasks / cron-like behavior

The first required built-in entries are:
- `hermes`
- `openclaw`

The implementation should be generic enough to add more later, for example by extending a dict/table/config-backed registry.

### 2A.2 Path auto-discovery intent

For mainstream agents, CoDesk should attempt to auto-detect likely paths instead of forcing the user to type them every time.

Examples of the desired behavior:
- on macOS, check conventional per-user directories such as `/Users/<user>/.agent-name`, or any other known mainstream default location for that agent
- if a known path exists, use it automatically
- if more than one candidate exists, show a concise choice list
- if no known path exists, fall back to a user prompt or blank config field

Important: the exact default paths may differ by platform and by agent release, so the implementation should centralize these assumptions in one place instead of scattering them across CLI code.

### 2A.3 Shared sync workspace defaulting

The setup flow should default-create the shared synchronization workspace even when the user provides minimal input.

That means the user should not need to hand-design:
- the workspace root name
- the blackboard subdirectory layout
- the reports directory layout

If the user does not supply a workspace path, CoDesk should choose a sensible default parent location and create the shared workspace there.

The exact default parent path may be platform-specific, but it must be deterministic and visible in the final CLI output.

---

## 3. Product framing

### 3.1 What CoDesk is

CoDesk is a **shared-workspace bootstrap and protocol tool** for two agents.

Its responsibilities are:
- define the workspace structure
- persist the collaboration contract
- generate collaboration artifacts
- produce prompts that teach each agent how to use the workspace

### 3.2 What CoDesk is not

At this phase, CoDesk is **not**:
- a full runtime orchestration system
- a messaging transport
- a memory database
- a GUI product
- a cloud sync engine

It is intentionally file-first and auditable.

---

## 4. Current implementation inventory

The next agent should understand the current code before changing it.

### 4.1 Current capabilities already present

Current code already supports:
- workspace initialization
- project record creation
- weekly record creation
- handoff record creation
- decision record creation
- workspace validation
- status summary
- weekly digest generation
- directional sync packet generation
- combined report generation

### 4.2 Current limitations relative to product goal

The current codebase does **not** yet provide:
- `setup` / `bootstrap` command
- durable workspace config file
- prompt generation for two agents
- normalized sync-frequency handling
- onboarding instructions for scheduled sync
- user-oriented single-command experience
- default-first agent registry / mainstream path auto-discovery

### 4.3 Architectural implication

This is important:

**The existing code is a valid data/model/reporting foundation.**
The next implementation phase should build on it, not replace it.

Do not throw away the current blackboard model unless a specific failure forces redesign.

---

## 5. Core product requirements

The next implementing agent must satisfy the following.

### Requirement A — One-command setup

There must be a new top-level CLI entry for the main user flow.
Recommended command name:

```text
setup
```

Alternative acceptable names:
- `bootstrap`
- `onboard`

But choose **one** canonical product entry point and keep it stable.

The command must support:
- interactive mode when arguments are omitted
- non-interactive mode when arguments are supplied
- a **default-first mode** where common values are inferred automatically and the user can accept them without manually entering every field

### Requirement B — Durable workspace config

The setup flow must write a config file inside the generated workspace.
Recommended path:

```text
assistant-sync/config.yaml
```

JSON is acceptable if YAML support is intentionally avoided, but YAML is preferred because it is human-readable for non-programmer inspection.

The config must include at least:
- workspace schema version
- project / collaboration name
- agent 1 name
- agent 2 name
- sync frequency
- workspace objective
- creation timestamp
- any assumptions needed by prompt generation

It should also be able to persist, when known:
- detected agent home / install / workspace paths
- whether each agent is expected to self-schedule recurring sync
- what defaults were auto-selected vs explicitly provided by the user

### Requirement C — Two copy-paste-ready prompts

The setup command must generate:
- Prompt A for Agent 1
- Prompt B for Agent 2

These prompts must be complete enough that an agent with no prior context can understand:
- its identity in this collaboration
- the counterpart identity
- the workspace path
- what directories and files matter
- what records it is allowed / expected to update
- what outputs it should generate on sync
- how often it should sync
- how to use the configured sync policy
- how to avoid overwriting the counterpart’s role
- what local agent-specific path(s) matter if CoDesk auto-discovered them

### Requirement D — Prompt text must encode scheduling expectations

The generated prompts must explicitly instruct each agent to create or use a recurring scheduled task if the platform supports it.

The prompt should not assume a specific scheduler implementation unless the agent platform is known.

The prompt should say something like:
- use your native scheduled task / cron capability if available
- follow the configured sync frequency
- on each sync run, inspect the shared workspace, update your side’s records, regenerate the relevant reports, and leave handoff material for the counterpart as needed

If CoDesk knows a given agent is expected to have scheduled-task capability, the generated prompt should say so explicitly and tell the agent to use that native capability.

### Requirement E — Preserve the file-first blackboard model

The generated prompts must teach agents to coordinate through the CoDesk workspace, not by assuming hidden shared memory.

The agents should treat the workspace as the source of truth for collaboration state.

---

## 6. Functional design

### 6.1 New setup flow

Recommended behavior for `codesk setup`:

#### Inputs to collect
At minimum, the system must be able to determine:
- shared workspace parent directory
- `agent-a`
- `agent-b`
- `sync-frequency`

Optional:
- `--objective`
- `--notes`
- `--seed-project-id`

But the preferred UX is that `agent-a`, `agent-b`, and workspace location are auto-filled for mainstream cases instead of always being asked interactively.

#### Interactive behavior
If required values are missing, prompt for them in terminal.
But prompting should be the fallback, not the primary design.
The goal is a beginner-friendly and low-friction experience where common values are inferred automatically.

#### Output artifacts
Setup should create:
- `assistant-sync/` workspace tree
- `assistant-sync/config.yaml`
- optionally one initial project record
- optionally initial report scaffolds if useful

The resulting config should capture both:
- the shared workspace path used for synchronization
- any auto-discovered mainstream agent paths that will help generated prompts be more concrete

#### Final terminal output
Must print:
- workspace path
- config path
- short next-step instructions
- prompt A block
- prompt B block

---

## 7. Recommended config schema

The exact schema may evolve, but the next iteration should start from something close to this:

```yaml
schema_version: 1
created_at: 2026-04-17T13:00:00Z
project_name: CoDesk dogfood rollout
objective: Keep Hermes and OpenClaw aligned on implementation progress
sync:
  frequency: daily
  guidance: "Run one sync at least once per day"
agents:
  a:
    name: hermes
    role: primary
    detected_paths:
      home: /Users/example/.hermes
  b:
    name: openclaw
    role: counterpart
    detected_paths:
      home: /Users/example/.openclaw
workspace:
  root_name: assistant-sync
  shared_sync_root: /absolute/path/to/assistant-sync
  blackboard_dir: blackboard
  reports_dir: shared/reports
bootstrap:
  seed_project_id: proj-codesk
  user_notes: "Prefer concise updates and explicit handoffs"
defaults:
  used_default_agents: true
  used_auto_discovered_paths: true
```

### Schema rules
- Keep versioned.
- Keep human-editable.
- Do not overdesign.
- Only persist fields actually needed by setup, prompt generation, or later report flows.

---

## 8. Prompt generation requirements

### 8.1 Prompt design goals

The generated prompt must be:
- self-contained
- operational
- explicit about file paths
- explicit about sync cadence
- explicit about record-writing behavior
- robust enough that a fresh agent can act without hidden context

### 8.2 Each prompt must include

For each agent, the prompt should mention:
- **who you are**
- **who the counterpart is**
- **workspace root absolute path**
- **purpose of the collaboration**
- **sync frequency expectation**
- **any agent-specific local path CoDesk discovered that is relevant to your environment**
- **what to read before each sync**
- **what files to update**
- **what reports to regenerate**
- **when to create a handoff**
- **how to treat the blackboard as source of truth**

### 8.3 Prompt content outline

Each generated prompt should approximately follow this structure:

1. identity and collaboration objective
2. workspace path
3. important directories
4. expected routine per sync cycle
5. expected report-generation commands
6. handoff rules
7. scheduling instruction
8. first action to take after reading the prompt

### 8.4 First-run action

Each prompt should instruct the receiving agent to do a first-run verification such as:
- inspect the workspace
- confirm config values
- generate or inspect current reports
- acknowledge readiness

This matters because it reduces ambiguity after copy/paste onboarding.

---

## 9. Sync model the prompts should teach

The product intent is a recurring loop, not one-shot file generation.

Each sync cycle should conceptually be:

1. read workspace config
2. inspect blackboard records relevant to the collaboration
3. inspect latest reports
4. update your own weekly/project/handoff material as needed
5. regenerate shared reports
6. leave counterpart-facing handoff content when needed
7. wait until next scheduled sync

The prompt should guide the agent to behave like a disciplined participant in this loop.

---

## 10. CLI/API design recommendations

The next agent does not need to follow this exactly, but this is the preferred shape.

### 10.1 New CLI commands
Recommended additions:

- `setup`
- `print-prompts`
- `show-config`
- `detect-agents` (optional helper command if path discovery needs explicit debugging)

#### `setup`
Creates workspace + config + prints prompts.

#### `print-prompts`
Reads existing config and prints both prompts again.
This is important because the user may lose the first output.

#### `show-config`
Displays parsed config summary for debugging.

### 10.2 Existing commands to preserve
Do not remove current commands:
- `init`
- `new-project`
- `new-weekly`
- `new-handoff`
- `new-decision`
- `validate`
- `status`
- `weekly-digest`
- `sync-packet`
- `generate-reports`

The setup flow should be built **on top of** the existing lower-level commands/functions.

---

## 11. File layout recommendations for the next phase

A reasonable implementation may add files like:

- `src/codesk/config.py`
- `src/codesk/bootstrap.py`
- `src/codesk/agents.py`
- `src/codesk/prompts.py`
- `tests/test_setup.py`
- `tests/test_agents.py`
- `tests/test_prompts.py`
- `tests/test_config.py`

This is a recommendation, not a hard requirement.

But the next implementation should keep responsibilities separated:
- config parsing/writing
- setup/bootstrap logic
- mainstream agent registry + path discovery
- prompt rendering
- CLI wiring

---

## 12. Testing expectations

The next implementing agent should add tests for at least:

### 12.1 Setup command
- creates workspace
- writes config
- prints prompt blocks
- supports non-interactive arguments

### 12.2 Config layer
- writes deterministic config
- reads config back correctly
- rejects malformed config cleanly if validation is added

### 12.3 Prompt generation
- prompt A contains correct agent identity and counterpart
- prompt B contains correct inverse identity and counterpart
- both prompts include workspace path and sync frequency
- prompt text includes scheduling instruction

### 12.4 Agent detection
- known mainstream agent paths are checked in a deterministic order
- detection gracefully handles missing paths
- multiple candidate paths produce deterministic behavior or a clear prompt path

### 12.5 Regression
- existing commands still pass current tests

---

## 13. Design constraints and guardrails

### Guardrail 1 — Keep the product file-first
Do not add a database.
Do not add hidden agent state.
Do not make the system depend on a server.

### Guardrail 2 — Optimize for explicitness
The main product value is clarity and low-friction agent collaboration.
Prefer explicit config and explicit prompts over magic.

### Guardrail 3 — Avoid overfitting to one agent runtime
The product may be used with Hermes + OpenClaw today, but the CoDesk core should stay generic enough to support “Agent A / Agent B” style collaboration.

This means: default to Hermes + OpenClaw today, but implement these defaults through a registry/extension interface rather than hardcoding product logic only for those two forever.

### Guardrail 4 — Preserve inspectability
A human should be able to read the workspace and understand what is happening.

### Guardrail 5 — Keep the first productized step small
The immediate goal is not a complete autonomous orchestration system.
The immediate goal is a **setup-and-bootstrap product surface**.

---

## 14. Definition of done for the next implementation phase

The next phase should be considered complete when a new user can:

1. run one command
2. answer a small number of setup questions if needed
3. receive a created workspace and config file
4. receive two prompts
5. paste those prompts into two agents
6. have both agents understand the intended shared-workspace sync protocol without extra human explanation

If the user still has to manually explain the collaboration protocol to the agents, the phase is **not done**.

---

## 15. Suggested implementation order

Recommended order for the next agent:

1. Add mainstream agent registry + path discovery helpers.
2. Add config model + read/write helpers.
3. Add setup/bootstrap service layer with default-first behavior.
4. Add prompt-rendering layer.
5. Wire new CLI commands.
6. Add tests.
7. Update README once behavior is stable.

---

## 16. Concrete examples of acceptable sync-frequency values

The first implementation can keep this simple. Supported values may include:
- `hourly`
- `daily`
- `weekly`
- `every 6h`
- `every 12h`
- `every weekday`

It is acceptable to store sync frequency as a plain string at first, as long as prompt generation preserves it accurately.

Do not block the whole feature on designing a perfect scheduling DSL.

---

## 17. Important product insight

The key missing feature is **not** better digest formatting.
The key missing feature is **bootstrap clarity plus default automation**.

The product will feel real when a user can run one command and immediately obtain:
- a workspace
- a contract
- two prompts

And, for common mainstream agents, this should happen with as little manual path/config entry as possible.

That is the core of the next milestone.

---

## 18. Relationship to existing MVP plan

The earlier MVP plan in `docs/plans/codesk-mvp.md` focused on:
- workspace skeleton
- records
- validation
- summary/indexing
- digest/report generation

That MVP foundation is still valid.

This design spec defines the **next layer above the MVP**:
- setup UX
- config contract
- agent bootstrap prompts
- mainstream agent default discovery

The next implementing agent should therefore treat this document as an **extension/specification layer on top of the MVP plan**, not as a replacement for the whole repository direction.

---

## 19. Handoff instruction to the next agent

If you are the next agent implementing CoDesk:

1. Read this spec fully.
2. Read the existing code in `src/codesk/`.
3. Preserve existing lower-level capabilities.
4. Build the new product-facing entry point around them.
5. Optimize for an end user who wants “one command + two prompts”.
6. Prefer default discovery and minimal prompting for mainstream agents.
7. Do not stop at internal plumbing; the CLI output experience is part of the feature.

---

## 20. Short version

If you only remember one sentence, remember this:

**CoDesk’s next milestone is to turn the existing shared-blackboard prototype into a default-first, one-command bootstrap tool that creates a shared workspace, auto-discovers mainstream agent defaults where possible, writes config, and emits two ready-to-paste agent prompts for recurring collaboration.**
