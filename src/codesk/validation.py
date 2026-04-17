"""Validation helpers for CoDesk records."""

from __future__ import annotations

from pathlib import Path

REQUIRED_FIELDS = {
    "projects": (
        "project_id",
        "title",
        "owner",
        "status",
        "updated_at",
        "summary",
        "next_actions",
        "risks",
        "source_pointers",
    ),
    "weekly": (
        "week",
        "assistant",
        "completed",
        "in_progress",
        "blockers",
        "needs_from_counterpart",
        "source_pointers",
    ),
    "handoffs": (
        "handoff_id",
        "from",
        "to",
        "project",
        "context_summary",
        "requested_action",
        "priority",
        "due_hint",
        "evidence",
    ),
    "decisions": (
        "decision_id",
        "date",
        "topic",
        "decision",
        "reasoning_summary",
        "affected_projects",
        "evidence",
    ),
}


def _parse_record(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def validate_workspace(workspace_root: str | Path) -> dict[str, object]:
    root = Path(workspace_root)
    errors: list[dict[str, str]] = []

    blackboard_root = root / "blackboard"
    for record_type, required_fields in REQUIRED_FIELDS.items():
        record_dir = blackboard_root / record_type
        if not record_dir.exists():
            continue
        for path in sorted(record_dir.glob("*.md")):
            record = _parse_record(path)
            for field in required_fields:
                if field not in record:
                    errors.append(
                        {"path": str(path), "field": field, "code": "missing_required_field"}
                    )
                elif record[field] == "":
                    errors.append(
                        {"path": str(path), "field": field, "code": "empty_required_field"}
                    )

    return {
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }
