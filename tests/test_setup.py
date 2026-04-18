from pathlib import Path

from codesk.bootstrap import SetupRequest, run_setup
from codesk.config import load_config


def test_run_setup_creates_workspace_and_config(tmp_path: Path) -> None:
    result = run_setup(SetupRequest(directory=tmp_path), env={}, home_path=tmp_path)

    assert result.workspace_path == (tmp_path / "assistant-sync").resolve()
    assert result.workspace_path.is_dir()
    assert result.config_path == result.workspace_path / "config.yaml"
    assert result.config_path.is_file()
    assert result.seed_project_path is None

    config = load_config(result.config_path)
    assert config["project_name"] == "Hermes × OpenClaw collaboration"
    assert config["objective"] == "Keep Hermes and OpenClaw aligned through the CoDesk shared workspace."
    assert config["sync"]["frequency"] == "daily"
    assert config["agents"]["a"]["name"] == "hermes"
    assert config["agents"]["b"]["name"] == "openclaw"


def test_run_setup_generates_initial_reports(tmp_path: Path) -> None:
    result = run_setup(SetupRequest(directory=tmp_path), env={}, home_path=tmp_path)

    assert result.weekly_digest_path == result.workspace_path / "shared" / "reports" / "weekly-digest.md"
    assert result.sync_packet_a_to_b_path == result.workspace_path / "shared" / "reports" / "sync-packet-hermes-to-openclaw.md"
    assert result.sync_packet_b_to_a_path == result.workspace_path / "shared" / "reports" / "sync-packet-openclaw-to-hermes.md"

    for report_path in result.report_paths.values():
        assert report_path.is_file()

    assert "# CoDesk Weekly Digest" in result.weekly_digest_path.read_text(encoding="utf-8")
    assert "from: hermes" in result.sync_packet_a_to_b_path.read_text(encoding="utf-8")
    assert "from: openclaw" in result.sync_packet_b_to_a_path.read_text(encoding="utf-8")


def test_run_setup_can_seed_initial_project_record(tmp_path: Path) -> None:
    result = run_setup(
        SetupRequest(
            directory=tmp_path,
            project_name="Seeded collaboration",
            seed_project_id="proj-001",
        ),
        env={},
        home_path=tmp_path,
    )

    assert result.seed_project_path == result.workspace_path / "blackboard" / "projects" / "proj-001.md"
    assert result.seed_project_path.is_file()

    project_record = result.seed_project_path.read_text(encoding="utf-8")
    assert "project_id: proj-001" in project_record
    assert "title: Seeded collaboration" in project_record
    assert "owner: hermes" in project_record
    assert "status: active" in project_record

    sync_packet = result.sync_packet_a_to_b_path.read_text(encoding="utf-8")
    assert "proj-001 | active | Seeded collaboration" in sync_packet


def test_run_setup_uses_defaults_when_request_fields_omitted(tmp_path: Path) -> None:
    result = run_setup(SetupRequest(directory=tmp_path), env={}, home_path=tmp_path)

    config = load_config(result.config_path)

    assert config["defaults"] == {
        "used_default_agents": True,
        "used_default_project_name": True,
        "used_default_objective": True,
        "used_default_sync_frequency": True,
        "used_auto_discovered_paths": True,
    }
    assert result.seed_project_path is None
    assert list((result.workspace_path / "blackboard" / "projects").glob("*.md")) == []


def test_run_setup_returns_both_prompt_strings(tmp_path: Path) -> None:
    result = run_setup(SetupRequest(directory=tmp_path), env={}, home_path=tmp_path)

    assert list(result.prompts.keys()) == ["a", "b"]
    assert result.prompt_a == result.prompts["a"]
    assert result.prompt_b == result.prompts["b"]
    assert "You are Hermes" in result.prompt_a
    assert "Your counterpart is OpenClaw" in result.prompt_a
    assert "You are OpenClaw" in result.prompt_b
    assert "Your counterpart is Hermes" in result.prompt_b
    assert str(result.workspace_path) in result.prompt_a
    assert str(result.config_path) in result.prompt_b
