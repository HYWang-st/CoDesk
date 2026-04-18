from pathlib import Path

import yaml

from codesk.config import build_config, load_config, summarize_config, write_config


def _sample_config(shared_sync_root: Path) -> dict[str, object]:
    return build_config(
        project_name="Hermes × OpenClaw collaboration",
        objective="Keep Hermes and OpenClaw aligned through the CoDesk shared workspace.",
        sync_frequency="daily",
        agent_a_name="hermes",
        agent_b_name="openclaw",
        shared_sync_root=shared_sync_root,
        agent_a_detected_paths={"home": "/Users/example/.hermes"},
        agent_b_detected_paths={"home": "/Users/example/.openclaw"},
    )


def test_write_config_creates_yaml_file_with_expected_top_level_keys(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    output_path = write_config(config, tmp_path / "assistant-sync")

    assert output_path.name == "config.yaml"
    payload = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    assert list(payload.keys()) == [
        "schema_version",
        "created_at",
        "project_name",
        "objective",
        "sync",
        "agents",
        "workspace",
        "bootstrap",
        "defaults",
    ]
    assert payload["schema_version"] == 1
    assert Path(payload["workspace"]["shared_sync_root"]).is_absolute()


def test_load_config_round_trips_written_yaml(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")
    config_path = write_config(config, tmp_path / "assistant-sync")

    loaded = load_config(config_path)

    assert loaded["agents"] == config["agents"]
    assert loaded["objective"] == config["objective"]
    assert loaded["sync"]["frequency"] == config["sync"]["frequency"]


def test_summarize_config_renders_human_readable_summary(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    summary = summarize_config(config)

    assert "Hermes × OpenClaw collaboration" in summary
    assert "hermes" in summary
    assert "openclaw" in summary
    assert "daily" in summary


def test_load_config_handles_missing_optional_detected_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "assistant-sync" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        "schema_version: 1\n"
        "created_at: 2026-04-18T00:00:00Z\n"
        "project_name: Hermes x OpenClaw collaboration\n"
        "objective: Keep aligned.\n"
        "sync:\n"
        "  frequency: daily\n"
        "  guidance: Run one sync at least once per day.\n"
        "agents:\n"
        "  a:\n"
        "    name: hermes\n"
        "    display_name: Hermes\n"
        "    role: primary\n"
        "    supports_native_schedule: true\n"
        "    selection_source: default\n"
        "  b:\n"
        "    name: openclaw\n"
        "    display_name: OpenClaw\n"
        "    role: counterpart\n"
        "    supports_native_schedule: true\n"
        "    selection_source: default\n"
        "workspace:\n"
        "  root_name: assistant-sync\n"
        "  shared_sync_root: /tmp/assistant-sync\n"
        "  blackboard_dir: blackboard\n"
        "  reports_dir: shared/reports\n"
        "bootstrap:\n"
        "  seed_project_id: null\n"
        "  user_notes: ''\n"
        "defaults:\n"
        "  used_default_agents: true\n"
        "  used_default_project_name: true\n"
        "  used_default_objective: true\n"
        "  used_default_sync_frequency: true\n"
        "  used_auto_discovered_paths: true\n",
        encoding="utf-8",
    )

    loaded = load_config(config_path)

    assert loaded["agents"]["a"]["detected_paths"] == {}
    assert loaded["agents"]["b"]["detected_paths"] == {}
