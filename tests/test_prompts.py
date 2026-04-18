from pathlib import Path

from codesk.config import build_config
from codesk.prompts import render_agent_prompt, render_all_prompts


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


def test_render_agent_prompt_includes_identity_counterpart_and_workspace_path(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    prompt = render_agent_prompt(config, "a")

    assert "You are Hermes" in prompt
    assert "Your counterpart is OpenClaw" in prompt
    assert str((tmp_path / "assistant-sync").resolve()) in prompt

    expected_sections = [
        "## 1. Identity and collaboration objective",
        "## 2. Workspace path",
        "## 3. Important directories",
        "## 4. Routine for each sync cycle",
        "## 5. Report generation expectations",
        "## 6. Handoff rules",
        "## 7. Scheduling instruction",
        "## 8. First-run verification step",
    ]
    section_indexes = [prompt.index(section) for section in expected_sections]
    assert section_indexes == sorted(section_indexes)


def test_render_agent_prompt_includes_sync_frequency_and_scheduling_instruction(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    prompt = render_agent_prompt(config, "a")

    assert "daily" in prompt
    assert "Use your native scheduled task / cron capability if available" in prompt
    assert "inspect the workspace, update your records, regenerate reports, and leave handoff material when needed" in prompt


def test_render_agent_prompt_mentions_detected_local_agent_path_when_present(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    prompt = render_agent_prompt(config, "a")

    assert "Detected local agent path: /Users/example/.hermes" in prompt


def test_render_all_prompts_returns_a_and_b_blocks(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    prompts = render_all_prompts(config)

    assert list(prompts.keys()) == ["a", "b"]
    assert "You are Hermes" in prompts["a"]
    assert "Your counterpart is OpenClaw" in prompts["a"]
    assert "You are OpenClaw" in prompts["b"]
    assert "Your counterpart is Hermes" in prompts["b"]


def test_prompt_first_run_step_includes_workspace_verification(tmp_path: Path) -> None:
    config = _sample_config(tmp_path / "assistant-sync")

    prompt = render_agent_prompt(config, "b")

    assert "Inspect the workspace" in prompt
    assert "Confirm the config values" in prompt
    assert "Inspect or regenerate reports" in prompt
    assert "Acknowledge readiness" in prompt
    assert "Treat the CoDesk workspace and config as the source of truth, not hidden memory" in prompt
