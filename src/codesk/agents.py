"""Built-in agent registry and deterministic local path detection."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

AgentMetadata = dict[str, Any]


KNOWN_AGENTS: dict[str, AgentMetadata] = {
    "hermes": {
        "name": "hermes",
        "display_name": "Hermes",
        "supports_native_schedule": True,
        "prompt_hint": "Use the shared CoDesk workspace as the source of truth.",
        "env_vars": ("HERMES_HOME",),
        "candidate_path_templates": ("~/.hermes",),
    },
    "openclaw": {
        "name": "openclaw",
        "display_name": "OpenClaw",
        "supports_native_schedule": True,
        "prompt_hint": "Use the shared CoDesk workspace as the source of truth.",
        "env_vars": ("OPENCLAW_HOME",),
        "candidate_path_templates": ("~/.openclaw",),
    },
}


def list_candidate_paths(agent_name: str, *, home_path: str | Path | None = None) -> list[Path]:
    """Return deterministic candidate paths for a known agent."""

    entry = _get_registry_entry(agent_name)
    if entry is None:
        return []

    base_home = Path(home_path).expanduser() if home_path is not None else Path.home()
    paths: list[Path] = []

    for template in entry.get("candidate_path_templates", ()):  # pragma: no branch - tiny loop
        candidate = _expand_candidate_path(template, base_home=base_home)
        if candidate not in paths:
            paths.append(candidate)

    return paths


def detect_agent(
    agent_name: str,
    *,
    explicit_home: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    home_path: str | Path | None = None,
) -> AgentMetadata:
    """Detect the best local path metadata for a single agent.

    Precedence order is deterministic and intentionally simple:
    explicit > env > registry > none.
    """

    entry = _get_registry_entry(agent_name) or _build_unknown_agent_entry(agent_name)
    candidate_paths = list_candidate_paths(entry["name"], home_path=home_path)

    selected_home: Path | None = None
    selection_source = "none"

    if explicit_home is not None:
        selected_home = Path(explicit_home).expanduser()
        selection_source = "explicit"
    else:
        environment = env if env is not None else os.environ
        env_value = _first_present_env_value(entry.get("env_vars", ()), environment)
        if env_value:
            selected_home = Path(env_value).expanduser()
            selection_source = "env"
        else:
            for candidate in candidate_paths:
                if candidate.exists():
                    selected_home = candidate
                    selection_source = "registry"
                    break

    return {
        "name": entry["name"],
        "display_name": entry["display_name"],
        "supports_native_schedule": bool(entry.get("supports_native_schedule", True)),
        "prompt_hint": entry.get("prompt_hint", ""),
        "selection_source": selection_source,
        "detected_paths": {"home": str(selected_home)} if selected_home is not None else {},
        "candidate_paths": [str(path) for path in candidate_paths],
    }


def detect_agents(
    *,
    agent_a_name: str,
    agent_b_name: str,
    agent_a_home: str | Path | None = None,
    agent_b_home: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    home_path: str | Path | None = None,
) -> dict[str, AgentMetadata]:
    """Detect metadata for the two bootstrap slots used by CoDesk setup."""

    return {
        "a": detect_agent(
            agent_a_name,
            explicit_home=agent_a_home,
            env=env,
            home_path=home_path,
        ),
        "b": detect_agent(
            agent_b_name,
            explicit_home=agent_b_home,
            env=env,
            home_path=home_path,
        ),
    }


def _get_registry_entry(agent_name: str) -> AgentMetadata | None:
    return KNOWN_AGENTS.get(_normalize_agent_name(agent_name))


def _build_unknown_agent_entry(agent_name: str) -> AgentMetadata:
    name = _normalize_agent_name(agent_name)
    return {
        "name": name,
        "display_name": _display_name(name),
        "supports_native_schedule": True,
        "prompt_hint": "",
        "env_vars": (),
        "candidate_path_templates": (),
    }


def _normalize_agent_name(agent_name: str) -> str:
    return str(agent_name).strip().lower()


def _display_name(agent_name: str) -> str:
    if agent_name == "openclaw":
        return "OpenClaw"
    if agent_name == "hermes":
        return "Hermes"
    return agent_name.replace("-", " ").replace("_", " ").title()


def _first_present_env_value(env_vars: tuple[str, ...], env: Mapping[str, str]) -> str | None:
    for env_var in env_vars:
        value = env.get(env_var)
        if value:
            return value
    return None


def _expand_candidate_path(template: str | Path, *, base_home: Path) -> Path:
    value = str(template)
    if value == "~":
        return base_home
    if value.startswith("~/"):
        return base_home / value[2:]
    return Path(value).expanduser()


__all__ = ["KNOWN_AGENTS", "detect_agent", "detect_agents", "list_candidate_paths"]
