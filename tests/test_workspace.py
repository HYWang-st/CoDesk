from pathlib import Path

from codesk.templates import (
    create_decision_record,
    create_handoff_record,
    create_project_record,
    create_weekly_record,
)
from codesk.validation import validate_workspace
from codesk.workspace import EXPECTED_WORKSPACE_DIRS, WORKSPACE_ROOT_NAME, init_workspace


def _workspace_dirs(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_dir()
    }


def test_init_workspace_creates_expected_assistant_sync_tree(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    assert workspace_root == tmp_path / WORKSPACE_ROOT_NAME
    assert workspace_root.is_dir()
    assert _workspace_dirs(workspace_root) == {
        relative_path
        for relative_path in EXPECTED_WORKSPACE_DIRS
        if relative_path != Path(".")
    }


def test_init_workspace_is_idempotent(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    sentinel = workspace_root / "blackboard" / "projects" / "existing.md"
    sentinel.write_text("keep me\n", encoding="utf-8")

    second_root = init_workspace(tmp_path)

    assert second_root == workspace_root
    assert sentinel.read_text(encoding="utf-8") == "keep me\n"


def test_create_project_record_writes_required_fields(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    record_path = create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )

    assert record_path == workspace_root / "blackboard" / "projects" / "proj-alpha.md"
    content = record_path.read_text(encoding="utf-8")
    assert "project_id: proj-alpha" in content
    assert "title: Alpha rollout" in content
    assert "owner: hermes" in content
    assert "status: active" in content
    assert "summary:" in content
    assert "next_actions:" in content
    assert "risks:" in content
    assert "source_pointers:" in content


def test_create_weekly_handoff_and_decision_records_write_to_expected_locations(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    weekly_path = create_weekly_record(
        workspace_root,
        week="2026-W16",
        assistant="hermes",
    )
    handoff_path = create_handoff_record(
        workspace_root,
        handoff_id="handoff-001",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
    )
    decision_path = create_decision_record(
        workspace_root,
        decision_id="decision-001",
        topic="Sync cadence",
    )

    assert weekly_path == workspace_root / "blackboard" / "weekly" / "2026-W16-hermes.md"
    assert handoff_path == workspace_root / "blackboard" / "handoffs" / "handoff-001.md"
    assert decision_path == workspace_root / "blackboard" / "decisions" / "decision-001.md"


def test_validate_workspace_reports_missing_required_fields(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    project_path = workspace_root / "blackboard" / "projects" / "broken.md"
    project_path.write_text(
        "project_id: broken\n"
        "title:\n"
        "owner: hermes\n"
        "status: active\n"
        "updated_at:\n"
        "summary:\n"
        "next_actions:\n"
        "risks:\n"
        "source_pointers:\n",
        encoding="utf-8",
    )

    result = validate_workspace(workspace_root)

    assert result["ok"] is False
    assert result["error_count"] == 6
    assert result["errors"] == [
        {"path": str(project_path), "field": "title", "code": "empty_required_field"},
        {"path": str(project_path), "field": "updated_at", "code": "empty_required_field"},
        {"path": str(project_path), "field": "summary", "code": "empty_required_field"},
        {"path": str(project_path), "field": "next_actions", "code": "empty_required_field"},
        {"path": str(project_path), "field": "risks", "code": "empty_required_field"},
        {"path": str(project_path), "field": "source_pointers", "code": "empty_required_field"},
    ]
