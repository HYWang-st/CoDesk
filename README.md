# CoDesk

A lightweight agent collaboration layer for structured assistant-to-assistant sync.

## Quickstart

The recommended path is to bootstrap a ready-to-use workspace, config, prompts, and initial reports in one command:

```bash
PYTHONPATH=src python -m codesk.cli setup . \
  --project-name "Alpha rollout" \
  --objective "Ship the bootstrap workflow" \
  --agent-a OpenClaw \
  --agent-b Hermes \
  --sync-frequency weekly \
  --notes "Shared blackboard for coordination" \
  --seed-project-id proj-alpha
```

This creates `assistant-sync/`, writes the durable config to `assistant-sync/config.yaml`, generates the initial report files in `assistant-sync/shared/reports/`, and prints two ready-to-paste prompt blocks for the two agents.

The command output starts like this, then continues with the full prompt bodies:

```text
CoDesk workspace created at:
/path/to/project/assistant-sync

Config written to:
/path/to/project/assistant-sync/config.yaml

Next step:
1. Copy PROMPT A into Agent 1
2. Copy PROMPT B into Agent 2
3. Ask each agent to confirm its first sync run

===== PROMPT FOR AGENT 1 =====
...

===== PROMPT FOR AGENT 2 =====
...
```

Initial reports are created immediately so the workspace is inspectable after setup:

```text
assistant-sync/shared/reports/weekly-digest.md
assistant-sync/shared/reports/sync-packet-openclaw-to-hermes.md
assistant-sync/shared/reports/sync-packet-hermes-to-openclaw.md
```

To reprint the two bootstrap prompts from the existing config:

```bash
PYTHONPATH=src python -m codesk.cli print-prompts .
```

To inspect the saved collaboration config:

```bash
PYTHONPATH=src python -m codesk.cli show-config .
```

Example `show-config` output:

```text
Project: Alpha rollout
Objective: Ship the bootstrap workflow
Sync frequency: weekly
Agent A: openclaw
Agent B: hermes
Workspace: /path/to/project/assistant-sync
```

## Manual workspace commands

If you want to work at the lower-level file-first layer directly, the original commands remain available.

Initialize only the workspace tree in the current directory:

```bash
PYTHONPATH=src python -m codesk.cli init .
```

That command creates this tree:

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

Create records inside the shared blackboard:

```bash
PYTHONPATH=src python -m codesk.cli new-project . \
  --project-id proj-alpha \
  --title "Alpha rollout" \
  --owner hermes \
  --status active

PYTHONPATH=src python -m codesk.cli new-weekly . \
  --week 2026-W16 \
  --assistant hermes

PYTHONPATH=src python -m codesk.cli new-handoff . \
  --handoff-id handoff-001 \
  --from-assistant hermes \
  --to-assistant openclaw \
  --project proj-alpha

PYTHONPATH=src python -m codesk.cli new-decision . \
  --decision-id decision-001 \
  --topic "Weekly sync cadence"
```

Validate required fields across blackboard records:

```bash
PYTHONPATH=src python -m codesk.cli validate .
```

Show a compact collaboration summary:

```bash
PYTHONPATH=src python -m codesk.cli status .
```
