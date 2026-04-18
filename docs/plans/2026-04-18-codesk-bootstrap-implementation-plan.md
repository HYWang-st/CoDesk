# CoDesk Bootstrap Phase Implementation Plan

> **For implementer:** Use TDD throughout. Write failing test first. Watch it fail. Then implement.

**Goal:** Turn the current CoDesk MVP into a default-first bootstrap tool that creates a shared workspace, writes a durable collaboration config, auto-discovers mainstream agent defaults when possible, and emits two ready-to-paste prompts for recurring dual-agent collaboration.

**Architecture:** Build this as a thin product layer on top of the existing file-first primitives. Keep config, agent detection, prompt rendering, bootstrap orchestration, and CLI wiring as separate modules. Preserve all current lower-level commands and compose them into a new `setup` user flow rather than replacing them.

**Tech Stack:** Python 3.11+ (local execution should prefer `/usr/local/bin/python3`), `argparse`, `dataclasses`, `pathlib`, `datetime`, `pytest`, and `PyYAML>=6` for human-readable `config.yaml` support.

---

## 1. Why this document exists

This file is the **single-source implementation handoff** for the next CoDesk milestone.
A fresh implementer with no chat history should be able to:

1. read this file,
2. inspect the referenced repo files,
3. execute the task list in order,
4. verify progress with tests,
5. and ship the milestone without needing hidden context.

If this plan and the code ever diverge, update the plan before continuing.

---

## 2. Read this first when resuming with zero context

### Mandatory reading order
1. `docs/plans/2026-04-18-codesk-bootstrap-implementation-plan.md` ← this file
2. `docs/plans/codesk-product-design-spec.md`
3. `README.md`
4. `src/codesk/cli.py`
5. `src/codesk/workspace.py`
6. `src/codesk/templates.py`
7. `src/codesk/validation.py`
8. `src/codesk/indexing.py`
9. `src/codesk/digest.py`
10. `src/codesk/sync_packet.py`
11. `tests/`

### Baseline facts as of 2026-04-18
- Repo path: `/Users/starsama/Code/CoDesk`
- Current package name: `codesk`
- Current product state: MVP exists; bootstrap product layer does not
- Current core capabilities already work:
  - workspace init
  - project / weekly / handoff / decision record generation
  - validation
  - status summary
  - weekly digest generation
  - sync packet generation
  - combined report generation
- Baseline full test suite: **28 passing** (`PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`)

### Non-negotiable guardrails
- Do **not** remove or break existing commands.
- Keep CoDesk **file-first**; no database, server, or hidden runtime state.
- Do **not** implement scheduler execution in this phase.
- Prompts must teach agents to use the shared workspace as the source of truth.
- Keep the first productized milestone small and inspectable.

---

## 3. Scope of this milestone

### In scope
This phase must add:
1. `codesk setup` as the canonical product entry point
2. durable workspace config at `assistant-sync/config.yaml`
3. built-in mainstream agent registry with default-first detection for at least:
   - `hermes`
   - `openclaw`
4. prompt generation for both collaborating agents
5. `codesk print-prompts`
6. `codesk show-config`
7. automated tests for the above
8. README updates for the new flow

### Explicitly out of scope
Do **not** add in this phase:
- runtime scheduler backend
- direct agent-to-agent messaging transport
- hidden memory layer
- web UI
- database/vector store
- more than two-agent collaboration model
- automatic syncing with Hermes/OpenClaw internals

### Optional stretch work
Only after the core milestone is green and documented:
- `codesk detect-agents` debug helper
- small internal dedup/refactor of repeated record parsing helpers

---

## 4. Product decisions frozen for this implementation

These decisions are made here so the implementer does not need to re-decide them mid-flight.

### 4.1 Canonical command names
Implement these commands exactly:
- `setup`
- `print-prompts`
- `show-config`

Optional later:
- `detect-agents`

### 4.2 Setup defaults
`codesk setup` with **zero arguments** must succeed on the happy path.
Use these defaults:

- workspace parent directory: current directory (`.`)
- workspace root name: `assistant-sync`
- agent A: `hermes`
- agent B: `openclaw`
- sync frequency: `daily`
- project name: `Hermes × OpenClaw collaboration`
- objective: `Keep Hermes and OpenClaw aligned through the CoDesk shared workspace.`
- notes: empty string
- seed project id: omitted by default

### 4.3 Config format
Use YAML, not JSON, for the main milestone.
Rationale: the approved spec prefers human-editable `config.yaml`, and `PyYAML` is a small acceptable dependency for a product-facing bootstrap tool.

### 4.4 Detection rules
Agent-path detection order must be deterministic:
1. explicit CLI override path (if provided)
2. environment variable override
3. built-in registry candidate paths
4. fallback to no detected path

If multiple candidate paths exist:
- interactive TTY: prompt the user to choose
- non-interactive run: choose the first deterministic candidate and record that it was auto-selected

### 4.5 Setup output contract
`setup` must print:
1. workspace path
2. config path
3. short next-step instructions
4. prompt A block
5. prompt B block

Use this exact visible shape:

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

### 4.6 Reports during setup
`setup` should also write initial report files so the workspace is inspectable immediately after bootstrap:
- `shared/reports/weekly-digest.md`
- `shared/reports/sync-packet-<agent-a>-to-<agent-b>.md`
- `shared/reports/sync-packet-<agent-b>-to-<agent-a>.md`

Even if they are initially sparse, their presence helps onboarding.

---

## 5. Target architecture and file map

### New files to create
- `src/codesk/config.py`
- `src/codesk/agents.py`
- `src/codesk/prompts.py`
- `src/codesk/bootstrap.py`
- `tests/test_config.py`
- `tests/test_agents.py`
- `tests/test_prompts.py`
- `tests/test_setup.py`

### Existing files to modify
- `pyproject.toml`
- `README.md`
- `src/codesk/cli.py`

### Existing files to preserve as stable lower-level primitives
- `src/codesk/workspace.py`
- `src/codesk/templates.py`
- `src/codesk/validation.py`
- `src/codesk/indexing.py`
- `src/codesk/digest.py`
- `src/codesk/sync_packet.py`

### Optional refactor candidates (do not do before core green)
- factor repeated `_parse_record()` logic into one shared helper

---

## 6. Proposed module responsibilities

### `src/codesk/config.py`
Owns the config contract.

Implement:
- config dataclasses or typed dict-like structures
- deterministic YAML serialization
- config loading/parsing
- human-readable config summary rendering for `show-config`

Recommended public surface:
- `build_config(...)`
- `write_config(config, path)`
- `load_config(path)`
- `config_to_dict(config)`
- `summarize_config(config)`

### `src/codesk/agents.py`
Owns the built-in agent registry and path detection.

Implement:
- built-in registry entries for `hermes` and `openclaw`
- candidate-path expansion per platform
- deterministic detection helpers
- selection metadata explaining whether a path was explicit / env / auto-detected / absent

Recommended public surface:
- `KNOWN_AGENTS`
- `detect_agent(...)`
- `detect_agents(...)`
- `list_candidate_paths(...)`

### `src/codesk/prompts.py`
Owns prompt rendering for both agents.

Implement:
- prompt rendering from config only
- no CLI I/O in this module
- plain markdown/text prompt output
- prompt blocks that are self-contained and operational

Recommended public surface:
- `render_agent_prompt(config, slot)`
- `render_all_prompts(config)`

### `src/codesk/bootstrap.py`
Owns the orchestration logic for setup.

Implement:
- resolve defaults
- perform path detection
- initialize workspace
- optionally seed initial project record
- write config
- write initial reports
- render prompts
- return a structured setup result

Recommended public surface:
- `SetupRequest`
- `SetupResult`
- `run_setup(request)`

### `src/codesk/cli.py`
Owns argparse wiring and terminal output.

Implement:
- new subcommands wired to service functions
- minimal interactive fallback when ambiguity exists
- exact output formatting contract for `setup`

---

## 7. Config schema to implement

Use this as the exact starting schema unless a test reveals a concrete issue.

```yaml
schema_version: 1
created_at: 2026-04-18T12:30:00Z
project_name: Hermes × OpenClaw collaboration
objective: Keep Hermes and OpenClaw aligned through the CoDesk shared workspace.
sync:
  frequency: daily
  guidance: Run one sync at least once per day.
agents:
  a:
    name: hermes
    display_name: Hermes
    role: primary
    supports_native_schedule: true
    selection_source: default
    detected_paths:
      home: /Users/example/.hermes
  b:
    name: openclaw
    display_name: OpenClaw
    role: counterpart
    supports_native_schedule: true
    selection_source: default
    detected_paths:
      home: /Users/example/.openclaw
workspace:
  root_name: assistant-sync
  shared_sync_root: /absolute/path/to/assistant-sync
  blackboard_dir: blackboard
  reports_dir: shared/reports
bootstrap:
  seed_project_id: null
  user_notes: ""
defaults:
  used_default_agents: true
  used_default_project_name: true
  used_default_objective: true
  used_default_sync_frequency: true
  used_auto_discovered_paths: true
```

### Schema rules
- Keep field order deterministic.
- Always persist `schema_version` and `created_at`.
- `shared_sync_root` must be absolute.
- `seed_project_id` may be null.
- `detected_paths` may be empty, but the key should still exist.
- `selection_source` must be one of:
  - `explicit`
  - `env`
  - `auto-detected`
  - `default`
  - `none`

---

## 8. Prompt contract to implement

Every generated prompt must include these sections in order:

1. identity and collaboration objective
2. workspace path
3. important directories
4. routine for each sync cycle
5. report generation expectations
6. handoff rules
7. scheduling instruction
8. first-run verification step

### Prompt requirements
For each agent prompt, explicitly include:
- who the receiving agent is
- who the counterpart is
- absolute workspace root path
- purpose/objective
- configured sync frequency
- any detected local path relevant to that agent
- what to read before each sync
- which files the agent is expected to update
- when to leave a handoff for the counterpart
- instruction to treat the CoDesk workspace as source of truth

### First-run instruction text
The prompt should tell the agent to:
1. inspect the workspace,
2. confirm config values,
3. inspect or regenerate reports,
4. acknowledge readiness.

### Scheduling instruction text
Each prompt must say the equivalent of:
- use your native scheduled task / cron capability if available
- follow the configured sync frequency
- on each sync run, inspect the workspace, update your records, regenerate reports, and leave handoff material when needed

### Role boundaries
The prompt must also explicitly say:
- do not overwrite the counterpart’s role-specific updates unless correcting an obvious formatting issue
- use the blackboard/reports as shared coordination surfaces
- treat config + workspace as source of truth, not hidden memory

---

## 9. Working agreement for Kite + Codex collaboration

This section is for the actual execution workflow after planning.

### One-task-at-a-time rule
Do not let Codex work on multiple tasks from this plan at once.
Each task must complete its TDD loop and review gate before the next begins.

### Mandatory per-task loop
For every task below:
1. write or extend tests first
2. run only the targeted tests and confirm failure
3. implement the minimal code to pass
4. rerun targeted tests
5. rerun full suite
6. review diff against this plan
7. commit

### Suggested Codex dispatch template
Use this exact structure when delegating a task:

```text
Goal: [one-sentence task goal]
Context: You are implementing CoDesk bootstrap phase from docs/plans/2026-04-18-codesk-bootstrap-implementation-plan.md.
Files: [exact file paths]
Constraints:
- TDD first
- no scope creep
- preserve existing CLI commands
- keep the product file-first
Verify:
- run the listed targeted pytest command(s)
- run PYTHONPATH=src /usr/local/bin/python3 -m pytest -q
Task:
[paste the exact task section from this plan]
```

### Review gate after Codex returns
Kite must verify:
- task scope matches this plan
- tests cover the behavior promised
- CLI output still matches spec
- no unrelated refactor slipped in
- README/examples remain accurate if behavior changed

---

## 10. Detailed task list

The tasks below are ordered. Do them in sequence.

---

### Task 0: Baseline lock and branch hygiene

**Purpose:** Establish a clean, reproducible starting point before touching code.

**Files:**
- Read only: this plan, `docs/plans/codesk-product-design-spec.md`, existing `src/codesk/*`, existing `tests/*`

**Steps:**
1. Run the full suite:
   - `cd /Users/starsama/Code/CoDesk`
   - `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`
2. Confirm the suite is green before changing code.
3. Confirm no user-facing behavior has been changed outside this plan.
4. Create or switch to a feature branch if using git-flow locally.

**Verify:**
- Baseline test suite passes.

**Commit:**
- No commit needed unless branch metadata/worktree setup changes.

---

### Task 1: Add the config layer

**Goal:** Implement deterministic YAML config write/read helpers that can persist the bootstrap contract.

**Files:**
- Create: `src/codesk/config.py`
- Create: `tests/test_config.py`
- Modify: `pyproject.toml`

**Implementation requirements:**
- Add `PyYAML>=6` to project dependencies.
- Implement config creation, serialization, writing, loading, and summary rendering.
- Keep field order deterministic.
- Write absolute paths into config.
- Do not add CLI logic here.

**Tests to add first:**
- `test_write_config_creates_yaml_file_with_expected_top_level_keys`
- `test_load_config_round_trips_written_yaml`
- `test_summarize_config_renders_human_readable_summary`
- `test_load_config_handles_missing_optional_detected_paths`

**Expected assertions:**
- output file is named `config.yaml`
- `schema_version == 1`
- `shared_sync_root` is absolute
- round-trip load preserves agents, objective, and frequency
- summary output includes project name, agent names, and sync frequency

**Targeted test command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest tests/test_config.py -q`

**Full regression command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`

**Commit:**
- `git add pyproject.toml src/codesk/config.py tests/test_config.py && git commit -m "feat: add bootstrap config layer"`

---

### Task 2: Add the agent registry and deterministic path detection

**Goal:** Implement a built-in registry for `hermes` and `openclaw`, plus deterministic path detection metadata.

**Files:**
- Create: `src/codesk/agents.py`
- Create: `tests/test_agents.py`

**Implementation requirements:**
- Define built-in registry entries for `hermes` and `openclaw`.
- Support detection source precedence: explicit > env > registry > none.
- Candidate path expansion must use `Path.home()` or an injected home path for tests.
- Registry should carry:
  - canonical name
  - display name
  - supports native schedule
  - prompt hint (if useful)
  - candidate path templates
- Keep detection generic enough to add more agents later.

**Concrete detection defaults to implement:**
- `openclaw` candidates should include `~/.openclaw`
- `hermes` candidates should include `~/.hermes`
- environment variable overrides:
  - `OPENCLAW_HOME`
  - `HERMES_HOME`

**Tests to add first:**
- `test_detect_agent_prefers_explicit_path_over_env_and_registry`
- `test_detect_agent_uses_env_path_when_present`
- `test_detect_agent_falls_back_to_registry_candidate`
- `test_detect_agent_returns_none_when_no_candidate_exists`
- `test_registry_contains_hermes_and_openclaw`
- `test_detect_agents_returns_both_slots_with_metadata`

**Expected assertions:**
- selection source is recorded correctly
- registry detection order is deterministic
- absent paths do not crash setup
- registry is extendable and not hardcoded inside CLI

**Targeted test command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest tests/test_agents.py -q`

**Full regression command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`

**Commit:**
- `git add src/codesk/agents.py tests/test_agents.py && git commit -m "feat: add mainstream agent detection"`

---

### Task 3: Add prompt rendering

**Goal:** Generate two complete prompts from config only, with zero hidden context assumptions.

**Files:**
- Create: `src/codesk/prompts.py`
- Create: `tests/test_prompts.py`

**Implementation requirements:**
- Render prompt A and prompt B from loaded config.
- Prompts must be plain markdown/text blocks.
- Include all required sections from Section 8 of this plan.
- Prompts must invert identity/counterpart correctly between agent A and agent B.
- Keep CLI formatting out of this module.

**Tests to add first:**
- `test_render_agent_prompt_includes_identity_counterpart_and_workspace_path`
- `test_render_agent_prompt_includes_sync_frequency_and_scheduling_instruction`
- `test_render_agent_prompt_mentions_detected_local_agent_path_when_present`
- `test_render_all_prompts_returns_a_and_b_blocks`
- `test_prompt_first_run_step_includes_workspace_verification`

**Expected assertions:**
- prompt text contains receiving agent identity
- prompt text contains counterpart identity
- prompt text contains absolute workspace path
- prompt text contains sync frequency string exactly as configured
- prompt text contains first-run verification step
- prompt text instructs use of native scheduler if available

**Targeted test command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest tests/test_prompts.py -q`

**Full regression command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`

**Commit:**
- `git add src/codesk/prompts.py tests/test_prompts.py && git commit -m "feat: add agent bootstrap prompt rendering"`

---

### Task 4: Add the bootstrap/setup service layer

**Goal:** Orchestrate workspace creation, config writing, initial report generation, optional seed project creation, and prompt rendering in one pure service layer.

**Files:**
- Create: `src/codesk/bootstrap.py`
- Create: `tests/test_setup.py`
- Modify if necessary: `src/codesk/workspace.py`

**Implementation requirements:**
- Introduce a `SetupRequest` structure that accepts:
  - `directory`
  - `project_name`
  - `objective`
  - `agent_a`
  - `agent_b`
  - `sync_frequency`
  - `notes`
  - `seed_project_id`
  - `agent_a_home` override
  - `agent_b_home` override
- `run_setup(request)` must:
  1. resolve defaults
  2. detect agent paths
  3. initialize workspace
  4. optionally seed a project record
  5. write config
  6. write initial reports
  7. render prompts
  8. return a structured result with all produced paths/strings
- Seeded project behavior:
  - create only when `seed_project_id` is provided
  - use `project_name` as the project title
  - owner should default to agent A
  - status should default to `active`

**Tests to add first:**
- `test_run_setup_creates_workspace_and_config`
- `test_run_setup_generates_initial_reports`
- `test_run_setup_can_seed_initial_project_record`
- `test_run_setup_uses_defaults_when_request_fields_omitted`
- `test_run_setup_returns_both_prompt_strings`

**Expected assertions:**
- workspace directory exists
- `assistant-sync/config.yaml` exists
- initial report files exist
- seeded project file exists only when requested
- result object exposes config path, workspace path, and prompt strings

**Targeted test command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest tests/test_setup.py -q`

**Full regression command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`

**Commit:**
- `git add src/codesk/bootstrap.py tests/test_setup.py && git commit -m "feat: add one-command setup service"`

---

### Task 5: Wire the CLI commands and terminal UX

**Goal:** Expose the new product surface through `codesk setup`, `codesk print-prompts`, and `codesk show-config` while preserving all existing commands.

**Files:**
- Modify: `src/codesk/cli.py`
- Modify or extend tests in: `tests/test_cli_init.py`
- Optionally create: `tests/test_cli_setup.py` if the existing CLI test file becomes too crowded

**Implementation requirements:**
- Add argparse subcommands for:
  - `setup`
  - `print-prompts`
  - `show-config`
- `setup` should accept optional args:
  - positional `directory` default `.`
  - `--project-name`
  - `--objective`
  - `--agent-a`
  - `--agent-b`
  - `--sync-frequency`
  - `--notes`
  - `--seed-project-id`
  - `--agent-a-home`
  - `--agent-b-home`
- `print-prompts` should load existing config and print both prompt blocks again.
- `show-config` should load existing config and print the human-readable summary.
- Preserve existing CLI subcommands exactly.
- `setup` output must follow the exact contract from Section 4.5.

**Tests to add first:**
- `test_cli_setup_creates_workspace_config_and_prints_prompt_blocks`
- `test_cli_setup_accepts_non_interactive_arguments`
- `test_cli_print_prompts_reads_existing_config_and_reprints_both_blocks`
- `test_cli_show_config_prints_summary`
- `test_existing_cli_commands_still_work_after_new_commands_added`

**Expected assertions:**
- output contains workspace path line
- output contains config path line
- output contains both prompt delimiters exactly
- existing `init`, `status`, `weekly-digest`, `sync-packet`, etc. still pass

**Targeted test command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest tests/test_cli_init.py -q`

**Full regression command:**
- `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`

**Commit:**
- `git add src/codesk/cli.py tests/test_cli_init.py && git commit -m "feat: add bootstrap CLI commands"`

---

### Task 6: Update README for the new bootstrap flow

**Goal:** Make the repo self-explanatory for a new user after the feature lands.

**Files:**
- Modify: `README.md`

**Implementation requirements:**
- Add a new top-level quickstart section for `codesk setup`.
- Show the one-command happy path.
- Show how to rerun `print-prompts`.
- Show how to inspect `show-config`.
- Keep the older low-level commands documented; do not remove them.

**README content to add:**
- one-command setup example
- note that config is written to `assistant-sync/config.yaml`
- note that two prompts are printed for copy/paste into the two agents
- note that initial reports are generated
- advanced/manual commands remain available

**Verification:**
- run the example commands locally against a temp directory if needed
- ensure README examples match actual CLI argument names

**Commit:**
- `git add README.md && git commit -m "docs: document bootstrap setup workflow"`

---

### Task 7: Final acceptance pass

**Goal:** Prove the milestone works end-to-end and is ready for use by Kite + Codex.

**Files:**
- No required new files unless bugs are found

**Acceptance checklist:**
1. Full suite passes:
   - `PYTHONPATH=src /usr/local/bin/python3 -m pytest -q`
2. Manual smoke test in temp directory:
   - `PYTHONPATH=src /usr/local/bin/python3 -m codesk.cli setup /tmp/codesk-smoke`
3. Confirm generated artifacts exist:
   - `/tmp/codesk-smoke/assistant-sync/config.yaml`
   - `/tmp/codesk-smoke/assistant-sync/shared/reports/weekly-digest.md`
   - both sync-packet report files
4. Confirm terminal output includes two prompt blocks.
5. Confirm `print-prompts` works against the created workspace.
6. Confirm `show-config` prints a readable summary.
7. Confirm existing low-level commands still work against the created workspace.

**Done means:**
A new user can run one command, receive a workspace + config + prompts, paste those prompts into two agents, and those agents can understand how to collaborate through CoDesk without extra human explanation.

**Commit:**
- if no code changes are needed, no extra commit
- if bug fixes are required, make one final cleanup commit with a narrow message

---

## 11. Optional post-green stretch task

Only do this after Task 7 is fully green.

### Stretch Task A: Add `detect-agents` debug helper

**Purpose:** Provide a small diagnostic command for path detection behavior.

**Files:**
- Modify: `src/codesk/cli.py`
- Add tests if implemented

**Behavior:**
- print detected/default candidate info for `hermes` and `openclaw`
- do not block the milestone if omitted

---

## 12. Review checklist for any PR or handoff

Before declaring the phase done, verify all of the following:

### Product behavior
- `codesk setup` works with zero args
- config is YAML and readable
- prompts are self-contained
- setup writes initial reports
- no hidden runtime state was introduced

### Code quality
- responsibilities are separated by module
- existing commands are preserved
- new logic is covered by focused tests
- path detection is deterministic
- serialization is deterministic

### Documentation quality
- README matches real command names
- this plan still matches the implementation
- examples are copy/paste-safe

---

## 13. What to do if blocked

If you hit ambiguity while implementing, resolve it in this order:
1. this plan
2. `docs/plans/codesk-product-design-spec.md`
3. current tests and existing behavior
4. smallest file-first solution that preserves inspectability

If a design choice would expand scope materially, do **not** improvise a larger system. Record the issue in a decision note and keep the milestone small.

---

## 14. Not-for-this-phase backlog

Keep these out unless the user explicitly expands scope:
- scheduler backend owned by CoDesk
- multi-agent (>2) collaboration
- GUI/web app
- database/vector store
- syncing with live Hermes/OpenClaw internals
- generalized plugin system for agent runtimes
- record parser refactor unless needed for a bug fix

---

## 15. Short execution summary

If resuming fast, do this:

1. get baseline green
2. implement `config.py`
3. implement `agents.py`
4. implement `prompts.py`
5. implement `bootstrap.py`
6. wire CLI commands
7. update README
8. run full acceptance smoke test

That is the critical path.
