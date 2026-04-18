"""Bootstrap configuration helpers for CoDesk."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = 1
CONFIG_FILE_NAME = "config.yaml"
DEFAULT_BLACKBOARD_DIR = "blackboard"
DEFAULT_REPORTS_DIR = "shared/reports"
DEFAULT_SYNC_GUIDANCE = "Run one sync at least once per day."


ConfigDict = dict[str, Any]


def build_config(
    *,
    project_name: str,
    objective: str,
    sync_frequency: str,
    agent_a_name: str,
    agent_b_name: str,
    shared_sync_root: str | Path,
    agent_a_detected_paths: dict[str, str] | None = None,
    agent_b_detected_paths: dict[str, str] | None = None,
    agent_a_selection_source: str = "default",
    agent_b_selection_source: str = "default",
    agent_a_supports_native_schedule: bool = True,
    agent_b_supports_native_schedule: bool = True,
    seed_project_id: str | None = None,
    user_notes: str = "",
    used_default_agents: bool = True,
    used_default_project_name: bool = True,
    used_default_objective: bool = True,
    used_default_sync_frequency: bool = True,
    used_auto_discovered_paths: bool = True,
    created_at: str | None = None,
) -> ConfigDict:
    """Build the canonical CoDesk bootstrap config payload."""

    workspace_root = Path(shared_sync_root).expanduser().resolve()

    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "project_name": project_name,
        "objective": objective,
        "sync": {
            "frequency": sync_frequency,
            "guidance": DEFAULT_SYNC_GUIDANCE,
        },
        "agents": {
            "a": _build_agent_config(
                name=agent_a_name,
                role="primary",
                supports_native_schedule=agent_a_supports_native_schedule,
                selection_source=agent_a_selection_source,
                detected_paths=agent_a_detected_paths,
            ),
            "b": _build_agent_config(
                name=agent_b_name,
                role="counterpart",
                supports_native_schedule=agent_b_supports_native_schedule,
                selection_source=agent_b_selection_source,
                detected_paths=agent_b_detected_paths,
            ),
        },
        "workspace": {
            "root_name": workspace_root.name,
            "shared_sync_root": str(workspace_root),
            "blackboard_dir": DEFAULT_BLACKBOARD_DIR,
            "reports_dir": DEFAULT_REPORTS_DIR,
        },
        "bootstrap": {
            "seed_project_id": seed_project_id,
            "user_notes": user_notes,
        },
        "defaults": {
            "used_default_agents": used_default_agents,
            "used_default_project_name": used_default_project_name,
            "used_default_objective": used_default_objective,
            "used_default_sync_frequency": used_default_sync_frequency,
            "used_auto_discovered_paths": used_auto_discovered_paths,
        },
    }


def config_to_dict(config: ConfigDict) -> ConfigDict:
    """Return a normalized copy of ``config`` with deterministic ordering."""

    payload = deepcopy(config)
    payload["schema_version"] = int(payload.get("schema_version", SCHEMA_VERSION))
    payload["created_at"] = _normalize_created_at(payload.get("created_at"))

    workspace = dict(payload.get("workspace", {}))
    shared_sync_root = workspace.get("shared_sync_root", ".")
    workspace_root = Path(shared_sync_root).expanduser().resolve()
    workspace["root_name"] = workspace.get("root_name") or workspace_root.name
    workspace["shared_sync_root"] = str(workspace_root)
    workspace["blackboard_dir"] = workspace.get("blackboard_dir", DEFAULT_BLACKBOARD_DIR)
    workspace["reports_dir"] = workspace.get("reports_dir", DEFAULT_REPORTS_DIR)

    sync = dict(payload.get("sync", {}))
    sync["frequency"] = sync.get("frequency", "daily")
    sync["guidance"] = sync.get("guidance", DEFAULT_SYNC_GUIDANCE)

    bootstrap = dict(payload.get("bootstrap", {}))
    bootstrap["seed_project_id"] = bootstrap.get("seed_project_id")
    bootstrap["user_notes"] = bootstrap.get("user_notes", "")

    defaults = dict(payload.get("defaults", {}))
    defaults["used_default_agents"] = defaults.get("used_default_agents", True)
    defaults["used_default_project_name"] = defaults.get("used_default_project_name", True)
    defaults["used_default_objective"] = defaults.get("used_default_objective", True)
    defaults["used_default_sync_frequency"] = defaults.get("used_default_sync_frequency", True)
    defaults["used_auto_discovered_paths"] = defaults.get("used_auto_discovered_paths", True)

    agents = dict(payload.get("agents", {}))
    normalized_agents = {
        "a": _normalize_agent(agents.get("a", {}), role="primary"),
        "b": _normalize_agent(agents.get("b", {}), role="counterpart"),
    }

    return {
        "schema_version": payload["schema_version"],
        "created_at": payload["created_at"],
        "project_name": payload.get("project_name", ""),
        "objective": payload.get("objective", ""),
        "sync": sync,
        "agents": normalized_agents,
        "workspace": workspace,
        "bootstrap": bootstrap,
        "defaults": defaults,
    }


def write_config(config: ConfigDict, path: str | Path) -> Path:
    """Write ``config`` to ``config.yaml`` beneath ``path`` and return the file path."""

    target_path = Path(path).expanduser()
    if target_path.suffix == ".yaml":
        config_path = target_path
    else:
        config_path = target_path / CONFIG_FILE_NAME

    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = config_to_dict(config)
    config_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return config_path


def load_config(path: str | Path) -> ConfigDict:
    """Load and normalize a CoDesk config file."""

    config_path = Path(path).expanduser()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_to_dict(payload)


def summarize_config(config: ConfigDict) -> str:
    """Render a human-readable configuration summary."""

    payload = config_to_dict(config)
    return "\n".join(
        [
            f"Project: {payload['project_name']}",
            f"Objective: {payload['objective']}",
            f"Sync frequency: {payload['sync']['frequency']}",
            f"Agent A: {payload['agents']['a']['name']}",
            f"Agent B: {payload['agents']['b']['name']}",
            f"Workspace: {payload['workspace']['shared_sync_root']}",
        ]
    )


def _build_agent_config(
    *,
    name: str,
    role: str,
    supports_native_schedule: bool,
    selection_source: str,
    detected_paths: dict[str, str] | None,
) -> ConfigDict:
    return {
        "name": name,
        "display_name": _display_name(name),
        "role": role,
        "supports_native_schedule": supports_native_schedule,
        "selection_source": selection_source,
        "detected_paths": _normalize_detected_paths(detected_paths),
    }


def _normalize_agent(agent: dict[str, Any], *, role: str) -> ConfigDict:
    name = str(agent.get("name", ""))
    return {
        "name": name,
        "display_name": agent.get("display_name") or _display_name(name),
        "role": agent.get("role", role),
        "supports_native_schedule": bool(agent.get("supports_native_schedule", True)),
        "selection_source": agent.get("selection_source", "default"),
        "detected_paths": _normalize_detected_paths(agent.get("detected_paths")),
    }


def _normalize_detected_paths(detected_paths: Any) -> dict[str, str]:
    if not detected_paths:
        return {}

    return {str(key): str(value) for key, value in sorted(dict(detected_paths).items())}


def _display_name(name: str) -> str:
    if not name:
        return ""
    if name.lower() == "openclaw":
        return "OpenClaw"
    if name.lower() == "hermes":
        return "Hermes"
    return name.replace("-", " ").replace("_", " ").title()


def _normalize_created_at(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if value:
        return str(value)
    return _utc_now_iso()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
