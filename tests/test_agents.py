from pathlib import Path

from codesk.agents import KNOWN_AGENTS, detect_agent, detect_agents, list_candidate_paths


def test_detect_agent_prefers_explicit_path_over_env_and_registry(tmp_path: Path) -> None:
    registry_home = tmp_path / ".openclaw"
    registry_home.mkdir()
    explicit_home = tmp_path / "explicit-openclaw"

    detected = detect_agent(
        "openclaw",
        explicit_home=explicit_home,
        env={"OPENCLAW_HOME": str(tmp_path / "env-openclaw")},
        home_path=tmp_path,
    )

    assert detected["selection_source"] == "explicit"
    assert detected["detected_paths"] == {"home": str(explicit_home)}
    assert detected["candidate_paths"] == [str(registry_home)]


def test_detect_agent_uses_env_path_when_present(tmp_path: Path) -> None:
    registry_home = tmp_path / ".hermes"
    registry_home.mkdir()
    env_home = tmp_path / "env-hermes"

    detected = detect_agent(
        "hermes",
        env={"HERMES_HOME": str(env_home)},
        home_path=tmp_path,
    )

    assert detected["selection_source"] == "env"
    assert detected["detected_paths"] == {"home": str(env_home)}
    assert detected["candidate_paths"] == [str(registry_home)]


def test_detect_agent_falls_back_to_registry_candidate(tmp_path: Path) -> None:
    registry_home = tmp_path / ".openclaw"
    registry_home.mkdir()

    detected = detect_agent("openclaw", home_path=tmp_path)

    assert detected["selection_source"] == "registry"
    assert detected["detected_paths"] == {"home": str(registry_home)}
    assert detected["candidate_paths"] == [str(registry_home)]


def test_detect_agent_returns_none_when_no_candidate_exists(tmp_path: Path) -> None:
    detected = detect_agent("hermes", home_path=tmp_path)

    assert detected["selection_source"] == "none"
    assert detected["detected_paths"] == {}
    assert detected["candidate_paths"] == [str(tmp_path / ".hermes")]


def test_registry_contains_hermes_and_openclaw() -> None:
    assert list(KNOWN_AGENTS.keys()) == ["hermes", "openclaw"]
    assert KNOWN_AGENTS["hermes"]["display_name"] == "Hermes"
    assert KNOWN_AGENTS["hermes"]["env_vars"] == ("HERMES_HOME",)
    assert KNOWN_AGENTS["openclaw"]["display_name"] == "OpenClaw"
    assert KNOWN_AGENTS["openclaw"]["candidate_path_templates"] == ("~/.openclaw",)


def test_detect_agents_returns_both_slots_with_metadata(tmp_path: Path) -> None:
    hermes_home = tmp_path / ".hermes"
    hermes_home.mkdir()
    explicit_openclaw_home = tmp_path / "custom-openclaw"

    detected = detect_agents(
        agent_a_name="hermes",
        agent_b_name="openclaw",
        agent_b_home=explicit_openclaw_home,
        home_path=tmp_path,
    )

    assert list(detected.keys()) == ["a", "b"]
    assert detected["a"] == {
        "name": "hermes",
        "display_name": "Hermes",
        "supports_native_schedule": True,
        "prompt_hint": "Use the shared CoDesk workspace as the source of truth.",
        "selection_source": "registry",
        "detected_paths": {"home": str(hermes_home)},
        "candidate_paths": [str(hermes_home)],
    }
    assert detected["b"] == {
        "name": "openclaw",
        "display_name": "OpenClaw",
        "supports_native_schedule": True,
        "prompt_hint": "Use the shared CoDesk workspace as the source of truth.",
        "selection_source": "explicit",
        "detected_paths": {"home": str(explicit_openclaw_home)},
        "candidate_paths": [str(tmp_path / ".openclaw")],
    }


def test_list_candidate_paths_uses_injected_home_path(tmp_path: Path) -> None:
    assert list_candidate_paths("openclaw", home_path=tmp_path) == [tmp_path / ".openclaw"]
