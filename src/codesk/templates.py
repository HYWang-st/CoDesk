"""Template generation for CoDesk blackboard records."""

from __future__ import annotations

from datetime import datetime, UTC
from pathlib import Path


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_record(path: Path, fields: list[tuple[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" if value else f"{key}:" for key, value in fields]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def create_project_record(
    workspace_root: str | Path,
    *,
    project_id: str,
    title: str,
    owner: str,
    status: str,
) -> Path:
    root = Path(workspace_root)
    return _write_record(
        root / "blackboard" / "projects" / f"{project_id}.md",
        [
            ("project_id", project_id),
            ("title", title),
            ("owner", owner),
            ("status", status),
            ("updated_at", _timestamp()),
            ("summary", "TBD"),
            ("next_actions", "TBD"),
            ("risks", "TBD"),
            ("source_pointers", "TBD"),
        ],
    )


def create_weekly_record(
    workspace_root: str | Path,
    *,
    week: str,
    assistant: str,
    completed: str = "TBD",
    in_progress: str = "TBD",
    blockers: str = "TBD",
    needs_from_counterpart: str = "TBD",
    source_pointers: str = "TBD",
) -> Path:
    root = Path(workspace_root)
    return _write_record(
        root / "blackboard" / "weekly" / f"{week}-{assistant}.md",
        [
            ("week", week),
            ("assistant", assistant),
            ("completed", completed),
            ("in_progress", in_progress),
            ("blockers", blockers),
            ("needs_from_counterpart", needs_from_counterpart),
            ("source_pointers", source_pointers),
        ],
    )


def create_handoff_record(
    workspace_root: str | Path,
    *,
    handoff_id: str,
    from_assistant: str,
    to_assistant: str,
    project: str,
    context_summary: str = "TBD",
    requested_action: str = "TBD",
    priority: str = "normal",
    due_hint: str = "TBD",
    evidence: str = "TBD",
) -> Path:
    root = Path(workspace_root)
    return _write_record(
        root / "blackboard" / "handoffs" / f"{handoff_id}.md",
        [
            ("handoff_id", handoff_id),
            ("from", from_assistant),
            ("to", to_assistant),
            ("project", project),
            ("context_summary", context_summary),
            ("requested_action", requested_action),
            ("priority", priority),
            ("due_hint", due_hint),
            ("evidence", evidence),
        ],
    )


def create_decision_record(
    workspace_root: str | Path,
    *,
    decision_id: str,
    topic: str,
) -> Path:
    root = Path(workspace_root)
    return _write_record(
        root / "blackboard" / "decisions" / f"{decision_id}.md",
        [
            ("decision_id", decision_id),
            ("date", _timestamp().split("T", 1)[0]),
            ("topic", topic),
            ("decision", "TBD"),
            ("reasoning_summary", "TBD"),
            ("affected_projects", "TBD"),
            ("evidence", "TBD"),
        ],
    )
