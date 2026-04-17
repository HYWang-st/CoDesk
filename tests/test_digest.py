from pathlib import Path

from codesk.digest import build_weekly_digest_markdown, write_weekly_digest_report
from codesk.sync_packet import build_sync_packet_markdown, write_sync_packet_report
from codesk.templates import (
    create_decision_record,
    create_handoff_record,
    create_project_record,
    create_weekly_record,
)
from codesk.workspace import init_workspace


def test_build_weekly_digest_markdown_includes_counts_and_sections(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )
    create_weekly_record(
        workspace_root,
        week="2026-W16",
        assistant="hermes",
    )
    create_handoff_record(
        workspace_root,
        handoff_id="handoff-001",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
    )
    create_decision_record(
        workspace_root,
        decision_id="decision-001",
        topic="Weekly sync cadence",
    )

    digest = build_weekly_digest_markdown(workspace_root)

    assert "# CoDesk Weekly Digest" in digest
    assert "## Counts" in digest
    assert "- Projects: 1" in digest
    assert "- Weekly: 1" in digest
    assert "- Handoffs: 1" in digest
    assert "- Decisions: 1" in digest
    assert "## Latest Projects" in digest
    assert "- proj-alpha | active | hermes" in digest
    assert "## Recent Handoffs" in digest
    assert "- handoff-001 | hermes -> openclaw | proj-alpha" in digest
    assert "## Decisions" in digest
    assert "- decision-001 | Weekly sync cadence" in digest


def test_build_weekly_digest_markdown_handles_empty_workspace(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    digest = build_weekly_digest_markdown(workspace_root)

    assert "# CoDesk Weekly Digest" in digest
    assert "- Projects: 0" in digest
    assert "## Latest Projects" in digest
    assert "- None" in digest


def test_build_sync_packet_markdown_groups_counterpart_relevant_sections(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )
    create_weekly_record(
        workspace_root,
        week="2026-W16",
        assistant="hermes",
    )
    create_handoff_record(
        workspace_root,
        handoff_id="handoff-001",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
    )
    create_decision_record(
        workspace_root,
        decision_id="decision-001",
        topic="Weekly sync cadence",
    )

    packet = build_sync_packet_markdown(
        workspace_root,
        from_assistant="hermes",
        to_assistant="openclaw",
    )

    assert "# CoDesk Sync Packet" in packet
    assert "from: hermes" in packet
    assert "to: openclaw" in packet
    assert "## Active Projects" in packet
    assert "- proj-alpha | active | Alpha rollout" in packet
    assert "## My Weekly Updates" in packet
    assert "- 2026-W16 | hermes" in packet
    assert "## Open Handoffs For You" in packet
    assert "- handoff-001 | proj-alpha | priority=normal" in packet
    assert "## Recent Decisions You Should Know" in packet
    assert "- decision-001 | Weekly sync cadence" in packet


def test_build_sync_packet_markdown_handles_no_matching_records(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    packet = build_sync_packet_markdown(
        workspace_root,
        from_assistant="hermes",
        to_assistant="openclaw",
    )

    assert "# CoDesk Sync Packet" in packet
    assert "## Active Projects" in packet
    assert "- None" in packet
    assert "## Open Handoffs For You" in packet


def test_build_sync_packet_markdown_expands_weekly_and_handoff_details(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )
    create_weekly_record(
        workspace_root,
        week="2026-W16",
        assistant="hermes",
    )
    create_handoff_record(
        workspace_root,
        handoff_id="handoff-001",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
    )

    (workspace_root / "blackboard" / "weekly" / "2026-W16-hermes.md").write_text(
        "week: 2026-W16\n"
        "assistant: hermes\n"
        "completed: shipped packet skeleton\n"
        "in_progress: expanding human handoff content\n"
        "blockers: waiting for counterpart review\n"
        "needs_from_counterpart: review digest wording\n"
        "source_pointers: docs/weekly/W16.md\n",
        encoding="utf-8",
    )
    (workspace_root / "blackboard" / "handoffs" / "handoff-001.md").write_text(
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

    packet = build_sync_packet_markdown(
        workspace_root,
        from_assistant="hermes",
        to_assistant="openclaw",
    )

    assert "### 2026-W16" in packet
    assert "- Completed: shipped packet skeleton" in packet
    assert "- In progress: expanding human handoff content" in packet
    assert "- Blockers: waiting for counterpart review" in packet
    assert "- Need from openclaw: review digest wording" in packet
    assert "- Evidence: docs/weekly/W16.md" in packet
    assert "### handoff-001" in packet
    assert "- Context: packet structure is ready" in packet
    assert "- Requested action: review wording and add your progress" in packet
    assert "- Due: before friday sync" in packet
    assert "- Evidence: docs/packet/spec.md" in packet


def test_create_weekly_record_accepts_explicit_detail_fields(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    path = create_weekly_record(
        workspace_root,
        week="2026-W17",
        assistant="hermes",
        completed="shipped sync packet v1",
        in_progress="formalizing handoff fields",
        blockers="waiting for OpenClaw feedback",
        needs_from_counterpart="review packet tone",
        source_pointers="docs/weekly/W17.md",
    )
    content = path.read_text(encoding="utf-8")

    assert "completed: shipped sync packet v1" in content
    assert "in_progress: formalizing handoff fields" in content
    assert "blockers: waiting for OpenClaw feedback" in content
    assert "needs_from_counterpart: review packet tone" in content
    assert "source_pointers: docs/weekly/W17.md" in content


def test_create_handoff_record_accepts_explicit_detail_fields(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)

    path = create_handoff_record(
        workspace_root,
        handoff_id="handoff-002",
        from_assistant="hermes",
        to_assistant="openclaw",
        project="proj-alpha",
        context_summary="sync packet is ready for counterpart review",
        requested_action="add your side progress and risks",
        priority="high",
        due_hint="before friday sync",
        evidence="docs/packet/spec.md",
    )
    content = path.read_text(encoding="utf-8")

    assert "context_summary: sync packet is ready for counterpart review" in content
    assert "requested_action: add your side progress and risks" in content
    assert "priority: high" in content
    assert "due_hint: before friday sync" in content
    assert "evidence: docs/packet/spec.md" in content


def test_write_weekly_digest_report_creates_shared_report_file(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )

    report_path = write_weekly_digest_report(workspace_root)

    assert report_path.name == "weekly-digest.md"
    assert report_path.is_file()
    assert report_path.parent.name == "reports"
    assert "# CoDesk Weekly Digest" in report_path.read_text(encoding="utf-8")


def test_write_sync_packet_report_creates_named_report_file(tmp_path: Path) -> None:
    workspace_root = init_workspace(tmp_path)
    create_project_record(
        workspace_root,
        project_id="proj-alpha",
        title="Alpha rollout",
        owner="hermes",
        status="active",
    )

    report_path = write_sync_packet_report(
        workspace_root,
        from_assistant="hermes",
        to_assistant="openclaw",
    )

    assert report_path.name == "sync-packet-hermes-to-openclaw.md"
    assert report_path.is_file()
    assert report_path.parent.name == "reports"
    assert "# CoDesk Sync Packet" in report_path.read_text(encoding="utf-8")
