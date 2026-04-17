# CoDesk Implementation Plan

> **For Hermes:** supervise implementation and use Codex CLI inside this git repo for execution. Keep the project lightweight, file-first, auditable, and aligned with the approved Hermes × OpenClaw collaboration design.

**Goal:** Build an MVP collaboration layer that lets two assistants keep independent main memory while exchanging structured project sync, weekly summaries, handoff packets, and decision records inside a shared workspace.

**Architecture:** CoDesk will be a Python package plus a small CLI. The MVP will treat the collaboration area as a file-based workspace with opinionated Markdown/JSON templates and deterministic validation/indexing. The package will not implement full agent memory or orchestration; it will provide a shared blackboard/workspace layer with clean boundaries, metadata, and traceable records.

**Tech Stack:** Python 3.14, standard library (`pathlib`, `json`, `argparse`, `datetime`, `dataclasses`), pytest, Markdown/JSON file conventions.

---

## MVP scope

### In scope
1. Initialize a CoDesk workspace in any target directory.
2. Create the core folder structure for bilateral assistant collaboration.
3. Generate structured files/templates for:
   - project records
   - weekly sync records
   - handoff packets
   - decision ledger entries
4. Validate workspace records and surface missing/invalid metadata.
5. Build a small index/summary command that lists current collaboration state from file metadata.
6. Include tests for workspace initialization, record generation, validation, and indexing.

### Out of scope for MVP
- Real-time shared memory backend
- Direct agent-to-agent messaging transport
- Database/vector store
- Web UI
- Automatic sync with Hermes/OpenClaw internals

---

## Proposed repository skeleton

- `README.md`
- `pyproject.toml`
- `src/codesk/__init__.py`
- `src/codesk/cli.py`
- `src/codesk/models.py`
- `src/codesk/workspace.py`
- `src/codesk/templates.py`
- `src/codesk/validation.py`
- `src/codesk/indexing.py`
- `tests/test_cli_init.py`
- `tests/test_workspace.py`
- `tests/test_validation.py`
- `tests/test_indexing.py`
- `docs/plans/codesk-mvp.md`
- `.gitignore`

---

## Target workspace layout produced by the CLI

```text
assistant-sync/
  blackboard/
    projects/
    weekly/
    handoffs/
    decisions/
  hermes_to_openclaw/
  openclaw_to_hermes/
  references/
    source-pointers/
```

Notes:
- outbound-only writing model remains explicit
- `blackboard/` is the neutral shared layer
- records are summary-first and may include read-only source pointers

---

## Data model expectations

### Project record
Fields:
- `project_id`
- `title`
- `owner`
- `status`
- `updated_at`
- `summary`
- `next_actions`
- `risks`
- `source_pointers`

### Weekly sync record
Fields:
- `week`
- `assistant`
- `completed`
- `in_progress`
- `blockers`
- `needs_from_counterpart`
- `source_pointers`

### Handoff packet
Fields:
- `handoff_id`
- `from`
- `to`
- `project`
- `context_summary`
- `requested_action`
- `priority`
- `due_hint`
- `evidence`

### Decision record
Fields:
- `decision_id`
- `date`
- `topic`
- `decision`
- `reasoning_summary`
- `affected_projects`
- `evidence`

---

## Task breakdown

### Task 1: Create package scaffolding and project metadata
**Objective:** establish a clean Python package and test harness.

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `.gitignore`
- Create: `src/codesk/__init__.py`
- Create: `tests/__init__.py`

**Verification:**
- `python -m pytest tests/ -q` runs and discovers the test suite.

---

### Task 2: Add core data models
**Objective:** define minimal typed record structures for workspace artifacts.

**Files:**
- Create: `src/codesk/models.py`
- Test: `tests/test_workspace.py`

**Verification:**
- model constructors validate required fields
- serialization helpers produce stable dictionaries

---

### Task 3: Implement workspace initialization
**Objective:** create the `assistant-sync/` directory tree and seed placeholders.

**Files:**
- Create: `src/codesk/workspace.py`
- Test: `tests/test_workspace.py`

**Verification:**
- init command creates all expected directories
- re-running init is idempotent

---

### Task 4: Implement record templates
**Objective:** generate project/weekly/handoff/decision files with standard metadata.

**Files:**
- Create: `src/codesk/templates.py`
- Test: `tests/test_workspace.py`

**Verification:**
- generated files land in correct directories
- generated content includes required metadata fields

---

### Task 5: Implement validation
**Objective:** verify required metadata and report actionable errors.

**Files:**
- Create: `src/codesk/validation.py`
- Test: `tests/test_validation.py`

**Verification:**
- valid workspace returns success
- malformed files return structured validation errors

---

### Task 6: Implement indexing / summary view
**Objective:** summarize current collaboration state from file metadata.

**Files:**
- Create: `src/codesk/indexing.py`
- Test: `tests/test_indexing.py`

**Verification:**
- index command reports counts and latest updates
- summary includes projects, handoffs, and weekly sync presence

---

### Task 7: Implement CLI
**Objective:** expose `init`, `new-project`, `new-weekly`, `new-handoff`, `new-decision`, `validate`, and `status` commands.

**Files:**
- Create: `src/codesk/cli.py`
- Test: `tests/test_cli_init.py`

**Verification:**
- CLI subcommands execute successfully
- help text is clear and compact

---

### Task 8: Document the MVP
**Objective:** explain the concept, folder semantics, and usage examples.

**Files:**
- Update: `README.md`
- Create: `docs/plans/codesk-mvp.md`

**Verification:**
- README contains quickstart and command examples
- documented structure matches actual generated workspace

---

## Test strategy

Use strict TDD for implementation tasks:
1. write failing pytest case
2. run the targeted test and observe failure
3. implement the minimum code
4. re-run targeted test
5. run full test suite

Primary commands:
- `/usr/local/bin/python3 -m pytest tests/test_workspace.py -q`
- `/usr/local/bin/python3 -m pytest tests/test_validation.py -q`
- `/usr/local/bin/python3 -m pytest tests/test_indexing.py -q`
- `/usr/local/bin/python3 -m pytest tests/ -q`

---

## Risks and guardrails

- Keep MVP file-first; do not drift into agent-runtime coupling.
- Prefer deterministic templates and parsing over flexible but ambiguous formats.
- Preserve neutral naming (`assistant-sync`, `blackboard`) so future assistants can plug in.
- Source pointers must remain read-only references, not raw memory dumps.

---

## First implementation slice for Codex

Codex should start with the smallest vertical slice:
1. scaffold package + tests
2. implement workspace init
3. implement CLI `init`
4. prove with tests

After that, continue with template creation and validation.
