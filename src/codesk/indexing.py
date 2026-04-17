"""Read-only indexing helpers for CoDesk blackboard records."""

from __future__ import annotations

from pathlib import Path


def _parse_record(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def build_status_summary(workspace_root: str | Path) -> dict[str, object]:
    root = Path(workspace_root) / "blackboard"
    projects_dir = root / "projects"
    weekly_dir = root / "weekly"
    handoffs_dir = root / "handoffs"
    decisions_dir = root / "decisions"

    project_records = [_parse_record(path) for path in sorted(projects_dir.glob("*.md"))]
    project_records.sort(key=lambda record: record.get("updated_at", ""), reverse=True)
    handoff_records = [_parse_record(path) for path in sorted(handoffs_dir.glob("*.md"))]

    latest_projects = [
        {
            "project_id": record.get("project_id", ""),
            "status": record.get("status", ""),
            "owner": record.get("owner", ""),
        }
        for record in project_records[:5]
    ]
    recent_handoffs = [
        {
            "handoff_id": record.get("handoff_id", ""),
            "from": record.get("from", ""),
            "to": record.get("to", ""),
            "project": record.get("project", ""),
        }
        for record in handoff_records[:5]
    ]

    return {
        "counts": {
            "projects": len(list(projects_dir.glob("*.md"))),
            "weekly": len(list(weekly_dir.glob("*.md"))),
            "handoffs": len(list(handoffs_dir.glob("*.md"))),
            "decisions": len(list(decisions_dir.glob("*.md"))),
        },
        "latest_projects": latest_projects,
        "recent_handoffs": recent_handoffs,
    }
