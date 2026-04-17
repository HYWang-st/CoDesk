"""Counterpart-ready sync packet rendering for CoDesk."""

from __future__ import annotations

from pathlib import Path


REPORTS_DIR = Path("shared") / "reports"
SYNC_PACKET_BASENAME = "sync-packet"


def _parse_record(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _records(workspace_root: str | Path, record_type: str) -> list[dict[str, str]]:
    record_dir = Path(workspace_root) / "blackboard" / record_type
    return [_parse_record(path) for path in sorted(record_dir.glob("*.md"))]


def build_sync_packet_markdown(
    workspace_root: str | Path,
    *,
    from_assistant: str,
    to_assistant: str,
) -> str:
    projects = _records(workspace_root, "projects")
    weekly = [
        record
        for record in _records(workspace_root, "weekly")
        if record.get("assistant") == from_assistant
    ]
    handoffs = [
        record
        for record in _records(workspace_root, "handoffs")
        if record.get("from") == from_assistant and record.get("to") == to_assistant
    ]
    decisions = _records(workspace_root, "decisions")

    lines = [
        "# CoDesk Sync Packet",
        "",
        f"from: {from_assistant}",
        f"to: {to_assistant}",
        "",
        "## Active Projects",
    ]

    active_projects = [record for record in projects if record.get("status") == "active"]
    if active_projects:
        lines.extend(
            f"- {record.get('project_id', '')} | {record.get('status', '')} | {record.get('title', '')}"
            for record in active_projects[:5]
        )
    else:
        lines.append("- None")

    lines.extend(["", "## My Weekly Updates"])
    if weekly:
        for record in weekly[:5]:
            week = record.get("week", "")
            assistant = record.get("assistant", "")
            lines.append(f"- {week} | {assistant}")
            detailed_fields = [
                record.get("completed"),
                record.get("in_progress"),
                record.get("blockers"),
                record.get("needs_from_counterpart"),
                record.get("source_pointers"),
            ]
            if any(detailed_fields):
                lines.append(f"### {week}")
                if record.get("completed"):
                    lines.append(f"- Completed: {record['completed']}")
                if record.get("in_progress"):
                    lines.append(f"- In progress: {record['in_progress']}")
                if record.get("blockers"):
                    lines.append(f"- Blockers: {record['blockers']}")
                if record.get("needs_from_counterpart"):
                    lines.append(
                        f"- Need from {to_assistant}: {record['needs_from_counterpart']}"
                    )
                if record.get("source_pointers"):
                    lines.append(f"- Evidence: {record['source_pointers']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Open Handoffs For You"])
    if handoffs:
        for record in handoffs[:5]:
            handoff_id = record.get("handoff_id", "")
            lines.append(
                f"- {handoff_id} | {record.get('project', '')} | priority={record.get('priority', '')}"
            )
            detailed_fields = [
                record.get("context_summary"),
                record.get("requested_action"),
                record.get("due_hint"),
                record.get("evidence"),
            ]
            if any(detailed_fields):
                lines.append(f"### {handoff_id}")
                if record.get("context_summary"):
                    lines.append(f"- Context: {record['context_summary']}")
                if record.get("requested_action"):
                    lines.append(f"- Requested action: {record['requested_action']}")
                if record.get("due_hint"):
                    lines.append(f"- Due: {record['due_hint']}")
                if record.get("evidence"):
                    lines.append(f"- Evidence: {record['evidence']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Recent Decisions You Should Know"])
    if decisions:
        lines.extend(
            f"- {record.get('decision_id', '')} | {record.get('topic', '')}"
            for record in decisions[:5]
        )
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def write_sync_packet_report(
    workspace_root: str | Path,
    *,
    from_assistant: str,
    to_assistant: str,
) -> Path:
    root = Path(workspace_root)
    filename = f"{SYNC_PACKET_BASENAME}-{from_assistant}-to-{to_assistant}.md"
    report_path = root / REPORTS_DIR / filename
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_sync_packet_markdown(
            root,
            from_assistant=from_assistant,
            to_assistant=to_assistant,
        ),
        encoding="utf-8",
    )
    return report_path
