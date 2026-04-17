# CoDesk

A lightweight agent collaboration layer for structured assistant-to-assistant sync.

## Quickstart

Initialize a workspace in the current directory:

```bash
PYTHONPATH=src python -m codesk.cli init .
```

The command creates this tree:

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
