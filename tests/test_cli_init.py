from pathlib import Path

from codesk.cli import main
from codesk.workspace import EXPECTED_WORKSPACE_DIRS, WORKSPACE_ROOT_NAME


def test_cli_init_creates_expected_workspace_tree(
    tmp_path: Path, capsys
) -> None:
    exit_code = main(["init", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Initialized CoDesk workspace" in captured.out

    workspace_root = tmp_path / WORKSPACE_ROOT_NAME
    assert workspace_root.is_dir()
    assert {
        path.relative_to(workspace_root)
        for path in workspace_root.rglob("*")
        if path.is_dir()
    } == {
        relative_path
        for relative_path in EXPECTED_WORKSPACE_DIRS
        if relative_path != Path(".")
    }


def test_cli_new_project_creates_record(tmp_path: Path, capsys) -> None:
    exit_code = main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])
    captured = capsys.readouterr()

    record_path = tmp_path / WORKSPACE_ROOT_NAME / "blackboard" / "projects" / "proj-alpha.md"
    assert exit_code == 0
    assert str(record_path) in captured.out
    assert record_path.is_file()


def test_cli_validate_reports_errors_for_invalid_records(tmp_path: Path, capsys) -> None:
    workspace_root = tmp_path / WORKSPACE_ROOT_NAME
    project_dir = workspace_root / "blackboard" / "projects"
    project_dir.mkdir(parents=True)
    (project_dir / "broken.md").write_text(
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

    exit_code = main(["validate", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Validation failed" in captured.out
    assert "empty_required_field" in captured.out


def test_cli_status_prints_workspace_summary(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])
    main([
        "new-handoff",
        str(tmp_path),
        "--handoff-id",
        "handoff-001",
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--project",
        "proj-alpha",
    ])

    exit_code = main(["status", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Projects: 1" in captured.out
    assert "Handoffs: 1" in captured.out
    assert "proj-alpha | active | hermes" in captured.out
    assert "handoff-001 | hermes -> openclaw | proj-alpha" in captured.out


def test_cli_weekly_digest_prints_markdown_summary(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])
    main([
        "new-weekly",
        str(tmp_path),
        "--week",
        "2026-W16",
        "--assistant",
        "hermes",
    ])
    main([
        "new-handoff",
        str(tmp_path),
        "--handoff-id",
        "handoff-001",
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--project",
        "proj-alpha",
    ])
    main([
        "new-decision",
        str(tmp_path),
        "--decision-id",
        "decision-001",
        "--topic",
        "Weekly sync cadence",
    ])

    exit_code = main(["weekly-digest", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# CoDesk Weekly Digest" in captured.out
    assert "## Counts" in captured.out
    assert "- Projects: 1" in captured.out
    assert "## Latest Projects" in captured.out
    assert "- proj-alpha | active | hermes" in captured.out
    assert "## Recent Handoffs" in captured.out
    assert "- handoff-001 | hermes -> openclaw | proj-alpha" in captured.out
    assert "## Decisions" in captured.out
    assert "- decision-001 | Weekly sync cadence" in captured.out


def test_cli_sync_packet_prints_counterpart_ready_brief(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])
    main([
        "new-weekly",
        str(tmp_path),
        "--week",
        "2026-W16",
        "--assistant",
        "hermes",
    ])
    main([
        "new-handoff",
        str(tmp_path),
        "--handoff-id",
        "handoff-001",
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--project",
        "proj-alpha",
    ])
    main([
        "new-decision",
        str(tmp_path),
        "--decision-id",
        "decision-001",
        "--topic",
        "Weekly sync cadence",
    ])

    exit_code = main([
        "sync-packet",
        str(tmp_path),
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "# CoDesk Sync Packet" in captured.out
    assert "from: hermes" in captured.out
    assert "to: openclaw" in captured.out
    assert "## Active Projects" in captured.out
    assert "- proj-alpha | active | Alpha rollout" in captured.out
    assert "## My Weekly Updates" in captured.out
    assert "- 2026-W16 | hermes" in captured.out
    assert "## Open Handoffs For You" in captured.out
    assert "- handoff-001 | proj-alpha | priority=normal" in captured.out
    assert "## Recent Decisions You Should Know" in captured.out
    assert "- decision-001 | Weekly sync cadence" in captured.out


def test_cli_sync_packet_prints_human_handoff_details(tmp_path: Path, capsys) -> None:
    workspace_root = tmp_path / WORKSPACE_ROOT_NAME
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])
    main([
        "new-weekly",
        str(tmp_path),
        "--week",
        "2026-W16",
        "--assistant",
        "hermes",
    ])
    main([
        "new-handoff",
        str(tmp_path),
        "--handoff-id",
        "handoff-001",
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--project",
        "proj-alpha",
    ])

    weekly_path = workspace_root / "blackboard" / "weekly" / "2026-W16-hermes.md"
    weekly_path.write_text(
        "week: 2026-W16\n"
        "assistant: hermes\n"
        "completed: shipped packet skeleton\n"
        "in_progress: expanding human handoff content\n"
        "blockers: waiting for counterpart review\n"
        "needs_from_counterpart: review digest wording\n"
        "source_pointers: docs/weekly/W16.md\n",
        encoding="utf-8",
    )
    handoff_path = workspace_root / "blackboard" / "handoffs" / "handoff-001.md"
    handoff_path.write_text(
        "handoff_id: handoff-001\n"
        "from: hermes\n"
        "to: openclaw\n"
        "project: proj-alpha\n"
        "context_summary: packet structure is ready\n"
        "requested_action: review wording and add your progress\n"
        "priority: high\n"
        "due_hint: before friday sync\n"
        "evidence: docs/packet/spec.md\n",
        encoding="utf-8",
    )

    exit_code = main([
        "sync-packet",
        str(tmp_path),
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "### 2026-W16" in captured.out
    assert "- Completed: shipped packet skeleton" in captured.out
    assert "- In progress: expanding human handoff content" in captured.out
    assert "- Blockers: waiting for counterpart review" in captured.out
    assert "- Need from openclaw: review digest wording" in captured.out
    assert "### handoff-001" in captured.out
    assert "- Context: packet structure is ready" in captured.out
    assert "- Requested action: review wording and add your progress" in captured.out
    assert "- Due: before friday sync" in captured.out
    assert "- Evidence: docs/packet/spec.md" in captured.out


def test_cli_new_weekly_accepts_handoff_detail_flags(tmp_path: Path, capsys) -> None:
    exit_code = main([
        "new-weekly",
        str(tmp_path),
        "--week",
        "2026-W17",
        "--assistant",
        "hermes",
        "--completed",
        "shipped sync packet v1",
        "--in-progress",
        "formalizing handoff fields",
        "--blockers",
        "waiting for OpenClaw feedback",
        "--needs-from-counterpart",
        "review packet tone",
        "--source-pointers",
        "docs/weekly/W17.md",
    ])
    captured = capsys.readouterr()

    record_path = tmp_path / WORKSPACE_ROOT_NAME / "blackboard" / "weekly" / "2026-W17-hermes.md"
    content = record_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(record_path) in captured.out
    assert "completed: shipped sync packet v1" in content
    assert "in_progress: formalizing handoff fields" in content
    assert "blockers: waiting for OpenClaw feedback" in content
    assert "needs_from_counterpart: review packet tone" in content
    assert "source_pointers: docs/weekly/W17.md" in content


def test_cli_new_handoff_accepts_handoff_detail_flags(tmp_path: Path, capsys) -> None:
    exit_code = main([
        "new-handoff",
        str(tmp_path),
        "--handoff-id",
        "handoff-002",
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--project",
        "proj-alpha",
        "--context-summary",
        "sync packet is ready for counterpart review",
        "--requested-action",
        "add your side progress and risks",
        "--priority",
        "high",
        "--due-hint",
        "before friday sync",
        "--evidence",
        "docs/packet/spec.md",
    ])
    captured = capsys.readouterr()

    record_path = tmp_path / WORKSPACE_ROOT_NAME / "blackboard" / "handoffs" / "handoff-002.md"
    content = record_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert str(record_path) in captured.out
    assert "context_summary: sync packet is ready for counterpart review" in content
    assert "requested_action: add your side progress and risks" in content
    assert "priority: high" in content
    assert "due_hint: before friday sync" in content
    assert "evidence: docs/packet/spec.md" in content


def test_cli_weekly_digest_write_creates_report_file(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])

    exit_code = main([
        "weekly-digest",
        str(tmp_path),
        "--write",
    ])
    captured = capsys.readouterr()
    report_path = tmp_path / WORKSPACE_ROOT_NAME / "shared" / "reports" / "weekly-digest.md"

    assert exit_code == 0
    assert str(report_path) in captured.out
    assert report_path.is_file()
    assert "# CoDesk Weekly Digest" in report_path.read_text(encoding="utf-8")


def test_cli_sync_packet_write_creates_named_report_file(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])

    exit_code = main([
        "sync-packet",
        str(tmp_path),
        "--from-assistant",
        "hermes",
        "--to-assistant",
        "openclaw",
        "--write",
    ])
    captured = capsys.readouterr()
    report_path = (
        tmp_path
        / WORKSPACE_ROOT_NAME
        / "shared"
        / "reports"
        / "sync-packet-hermes-to-openclaw.md"
    )

    assert exit_code == 0
    assert str(report_path) in captured.out
    assert report_path.is_file()
    assert "# CoDesk Sync Packet" in report_path.read_text(encoding="utf-8")


def test_cli_generate_reports_writes_digest_and_bidirectional_packets(tmp_path: Path, capsys) -> None:
    main([
        "new-project",
        str(tmp_path),
        "--project-id",
        "proj-alpha",
        "--title",
        "Alpha rollout",
        "--owner",
        "hermes",
        "--status",
        "active",
    ])

    exit_code = main([
        "generate-reports",
        str(tmp_path),
        "--assistant-a",
        "hermes",
        "--assistant-b",
        "openclaw",
    ])
    captured = capsys.readouterr()

    workspace_root = tmp_path / WORKSPACE_ROOT_NAME
    digest_path = workspace_root / "shared" / "reports" / "weekly-digest.md"
    packet_ab = workspace_root / "shared" / "reports" / "sync-packet-hermes-to-openclaw.md"
    packet_ba = workspace_root / "shared" / "reports" / "sync-packet-openclaw-to-hermes.md"

    assert exit_code == 0
    assert str(digest_path) in captured.out
    assert str(packet_ab) in captured.out
    assert str(packet_ba) in captured.out
    assert digest_path.is_file()
    assert packet_ab.is_file()
    assert packet_ba.is_file()
