"""One-command bootstrap service for CoDesk setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from codesk.agents import AUTO_DETECTED_SOURCE, detect_agents
from codesk.config import build_config, write_config
from codesk.digest import write_weekly_digest_report
from codesk.prompts import render_all_prompts
from codesk.sync_packet import write_sync_packet_report
from codesk.templates import create_project_record
from codesk.workspace import init_workspace

DEFAULT_PROJECT_NAME = "Hermes × OpenClaw collaboration"
DEFAULT_OBJECTIVE = "Keep Hermes and OpenClaw aligned through the CoDesk shared workspace."
DEFAULT_AGENT_A = "hermes"
DEFAULT_AGENT_B = "openclaw"
DEFAULT_SYNC_FREQUENCY = "daily"
DEFAULT_NOTES = ""


@dataclass(slots=True)
class SetupRequest:
    directory: str | Path = "."
    project_name: str | None = None
    objective: str | None = None
    agent_a: str | None = None
    agent_b: str | None = None
    sync_frequency: str | None = None
    notes: str | None = None
    seed_project_id: str | None = None
    agent_a_home: str | Path | None = None
    agent_b_home: str | Path | None = None


@dataclass(slots=True)
class SetupResult:
    workspace_path: Path
    config_path: Path
    weekly_digest_path: Path
    sync_packet_a_to_b_path: Path
    sync_packet_b_to_a_path: Path
    seed_project_path: Path | None
    report_paths: dict[str, Path]
    prompt_a: str
    prompt_b: str
    prompts: dict[str, str]
    config: dict[str, Any]


@dataclass(slots=True)
class _ResolvedSetup:
    directory: Path
    project_name: str
    objective: str
    agent_a: str
    agent_b: str
    sync_frequency: str
    notes: str
    seed_project_id: str | None
    agent_a_home: str | Path | None
    agent_b_home: str | Path | None
    used_default_project_name: bool
    used_default_objective: bool
    used_default_agents: bool
    used_default_sync_frequency: bool


def run_setup(
    request: SetupRequest,
    *,
    env: Mapping[str, str] | None = None,
    home_path: str | Path | None = None,
) -> SetupResult:
    """Create a ready-to-use CoDesk workspace from a setup request."""

    resolved = _resolve_request(request)
    detected_agents = detect_agents(
        agent_a_name=resolved.agent_a,
        agent_b_name=resolved.agent_b,
        agent_a_home=resolved.agent_a_home,
        agent_b_home=resolved.agent_b_home,
        env=env,
        home_path=home_path,
    )

    workspace_path = init_workspace(resolved.directory).resolve()

    seed_project_path: Path | None = None
    if resolved.seed_project_id is not None:
        seed_project_path = create_project_record(
            workspace_path,
            project_id=resolved.seed_project_id,
            title=resolved.project_name,
            owner=detected_agents["a"]["name"],
            status="active",
        )

    config = build_config(
        project_name=resolved.project_name,
        objective=resolved.objective,
        sync_frequency=resolved.sync_frequency,
        agent_a_name=detected_agents["a"]["name"],
        agent_b_name=detected_agents["b"]["name"],
        shared_sync_root=workspace_path,
        agent_a_detected_paths=detected_agents["a"]["detected_paths"],
        agent_b_detected_paths=detected_agents["b"]["detected_paths"],
        agent_a_selection_source=detected_agents["a"]["selection_source"],
        agent_b_selection_source=detected_agents["b"]["selection_source"],
        agent_a_supports_native_schedule=detected_agents["a"]["supports_native_schedule"],
        agent_b_supports_native_schedule=detected_agents["b"]["supports_native_schedule"],
        seed_project_id=resolved.seed_project_id,
        user_notes=resolved.notes,
        used_default_agents=resolved.used_default_agents,
        used_default_project_name=resolved.used_default_project_name,
        used_default_objective=resolved.used_default_objective,
        used_default_sync_frequency=resolved.used_default_sync_frequency,
        used_auto_discovered_paths=_used_auto_discovered_paths(detected_agents),
    )
    config_path = write_config(config, workspace_path)

    weekly_digest_path = write_weekly_digest_report(workspace_path)
    sync_packet_a_to_b_path = write_sync_packet_report(
        workspace_path,
        from_assistant=detected_agents["a"]["name"],
        to_assistant=detected_agents["b"]["name"],
    )
    sync_packet_b_to_a_path = write_sync_packet_report(
        workspace_path,
        from_assistant=detected_agents["b"]["name"],
        to_assistant=detected_agents["a"]["name"],
    )

    prompts = render_all_prompts(config)

    return SetupResult(
        workspace_path=workspace_path,
        config_path=config_path,
        weekly_digest_path=weekly_digest_path,
        sync_packet_a_to_b_path=sync_packet_a_to_b_path,
        sync_packet_b_to_a_path=sync_packet_b_to_a_path,
        seed_project_path=seed_project_path,
        report_paths={
            "weekly_digest": weekly_digest_path,
            "sync_packet_a_to_b": sync_packet_a_to_b_path,
            "sync_packet_b_to_a": sync_packet_b_to_a_path,
        },
        prompt_a=prompts["a"],
        prompt_b=prompts["b"],
        prompts=prompts,
        config=config,
    )


def _resolve_request(request: SetupRequest) -> _ResolvedSetup:
    project_name, used_default_project_name = _coalesce_value(
        request.project_name,
        DEFAULT_PROJECT_NAME,
    )
    objective, used_default_objective = _coalesce_value(
        request.objective,
        DEFAULT_OBJECTIVE,
    )
    agent_a, agent_a_defaulted = _coalesce_value(request.agent_a, DEFAULT_AGENT_A)
    agent_b, agent_b_defaulted = _coalesce_value(request.agent_b, DEFAULT_AGENT_B)
    sync_frequency, used_default_sync_frequency = _coalesce_value(
        request.sync_frequency,
        DEFAULT_SYNC_FREQUENCY,
    )
    notes, _ = _coalesce_value(request.notes, DEFAULT_NOTES)
    seed_project_id = _normalize_optional_string(request.seed_project_id)

    return _ResolvedSetup(
        directory=Path(request.directory).expanduser(),
        project_name=project_name,
        objective=objective,
        agent_a=agent_a,
        agent_b=agent_b,
        sync_frequency=sync_frequency,
        notes=notes,
        seed_project_id=seed_project_id,
        agent_a_home=request.agent_a_home,
        agent_b_home=request.agent_b_home,
        used_default_project_name=used_default_project_name,
        used_default_objective=used_default_objective,
        used_default_agents=agent_a_defaulted and agent_b_defaulted,
        used_default_sync_frequency=used_default_sync_frequency,
    )


def _coalesce_value(value: str | None, default: str) -> tuple[str, bool]:
    normalized = _normalize_optional_string(value)
    if normalized is None:
        return default, True
    return normalized, False


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _used_auto_discovered_paths(detected_agents: dict[str, dict[str, Any]]) -> bool:
    selection_sources = {
        detected_agents["a"]["selection_source"],
        detected_agents["b"]["selection_source"],
    }
    return selection_sources <= {AUTO_DETECTED_SOURCE, "none"}


__all__ = ["SetupRequest", "SetupResult", "run_setup"]
