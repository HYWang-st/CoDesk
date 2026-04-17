from pathlib import Path

from codesk.indexing import build_status_summary
from codesk.templates import create_handoff_record, create_project_record, create_weekly_record
from codesk.workspace import init_workspace


def test_build_status_summary_counts_records_and_lists_latest_projects(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )
    create_project_record(
        workspace_root,
        project_id="proj-beta",
        title="Beta migration",
        owner="openclaw",
        status="blocked",
    )
    create_handoff_record(
        workspace_root,
        handoff_id="handoff-001",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
    )
    create_weekly_record(
        workspace_root,
        week="2026-W16",
        assistant="hermes",
    )

    summary = build_status_summary(workspace_root)

    assert summary["counts"] == {
        "projects": 2,
        "weekly": 1,
        "handoffs": 1,
        "decisions": 0,
    }
    assert summary["latest_projects"][0]["project_id"] == "proj-alpha"
    assert summary["latest_projects"][0]["status"] == "active"
    assert summary["latest_projects"][0]["owner"] == "hermes"
    assert summary["recent_handoffs"] == [
        {
            "handoff_id": "handoff-001",
            "from": "hermes",
            "to": "openclaw",
            "project": "proj-alpha",
        }
    ]


def test_build_status_summary_handles_empty_workspace(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    summary = build_status_summary(workspace_root)

    assert summary == {
        "counts": {
            "projects": 0,
            "weekly": 0,
            "handoffs": 0,
            "decisions": 0,
        },
        "latest_projects": [],
        "recent_handoffs": [],
    }
