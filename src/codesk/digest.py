"""Weekly digest rendering for CoDesk blackboard records."""

from __future__ import annotations

from pathlib import Path

from codesk.indexing import build_status_summary


REPORTS_DIR = Path("shared") / "reports"
WEEKLY_DIGEST_FILENAME = "weekly-digest.md"


def _parse_record(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def _decision_records(workspace_root: str | Path) -> list[dict[str, str]]:
    decisions_dir = Path(workspace_root) / "blackboard" / "decisions"
    return [_parse_record(path) for path in sorted(decisions_dir.glob("*.md"))]


def build_weekly_digest_markdown(workspace_root: str | Path) -> str:
    summary = build_status_summary(workspace_root)
    counts = summary["counts"]
    latest_projects = summary["latest_projects"]
    recent_handoffs = summary["recent_handoffs"]
    decisions = _decision_records(workspace_root)

    lines = [
        "# CoDesk Weekly Digest",
        "",
        "## Counts",
        f"- Projects: {counts['projects']}",
        f"- Weekly: {counts['weekly']}",
        f"- Handoffs: {counts['handoffs']}",
        f"- Decisions: {counts['decisions']}",
        "",
        "## Latest Projects",
    ]

    if latest_projects:
        lines.extend(
            f"- {project['project_id']} | {project['status']} | {project['owner']}"
            for project in latest_projects
        )
    else:
        lines.append("- None")

    lines.extend(["", "## Recent Handoffs"])
    if recent_handoffs:
        lines.extend(
            f"- {handoff['handoff_id']} | {handoff['from']} -> {handoff['to']} | {handoff['project']}"
            for handoff in recent_handoffs
        )
    else:
        lines.append("- None")

    lines.extend(["", "## Decisions"])
    if decisions:
        lines.extend(
            f"- {decision.get('decision_id', '')} | {decision.get('topic', '')}"
            for decision in decisions[:5]
        )
    else:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def write_weekly_digest_report(workspace_root: str | Path) -> Path:
    root = Path(workspace_root)
    report_path = root / REPORTS_DIR / WEEKLY_DIGEST_FILENAME
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_weekly_digest_markdown(root), encoding="utf-8")
    return report_path
