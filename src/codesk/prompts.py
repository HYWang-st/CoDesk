"""Bootstrap prompt rendering for CoDesk agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from codesk.config import CONFIG_FILE_NAME, config_to_dict

ConfigDict = dict[str, Any]


def render_agent_prompt(config: ConfigDict, slot: str) -> str:
    """Render the full bootstrap prompt for agent slot ``a`` or ``b``."""

    payload = config_to_dict(config)
    normalized_slot = _normalize_slot(slot)
    counterpart_slot = "b" if normalized_slot == "a" else "a"

    agent = payload["agents"][normalized_slot]
    counterpart = payload["agents"][counterpart_slot]

    workspace_root = Path(payload["workspace"]["shared_sync_root"]).expanduser().resolve()
    config_path = workspace_root / CONFIG_FILE_NAME
    blackboard_dir = workspace_root / payload["workspace"]["blackboard_dir"]
    reports_dir = workspace_root / payload["workspace"]["reports_dir"]
    weekly_digest_path = reports_dir / "weekly-digest.md"
    incoming_sync_packet = reports_dir / f"sync-packet-{counterpart['name']}-to-{agent['name']}.md"
    outgoing_sync_packet = reports_dir / f"sync-packet-{agent['name']}-to-{counterpart['name']}.md"

    detected_home = agent.get("detected_paths", {}).get("home")
    local_path_line = (
        f"Detected local agent path: {detected_home}"
        if detected_home
        else "Detected local agent path: none recorded"
    )

    return "\n".join(
        [
            "## 1. Identity and collaboration objective",
            f"You are {agent['display_name']}.",
            f"Your counterpart is {counterpart['display_name']}.",
            f"Collaboration objective: {payload['objective']}",
            "Treat the CoDesk workspace and config as the source of truth, not hidden memory.",
            "",
            "## 2. Workspace path",
            f"Shared workspace root: {workspace_root}",
            f"Config file: {config_path}",
            local_path_line,
            "",
            "## 3. Important directories",
            f"- Blackboard: {blackboard_dir}",
            f"- Reports: {reports_dir}",
            f"- Weekly digest: {weekly_digest_path}",
            f"- Incoming sync packet to read: {incoming_sync_packet}",
            f"- Outgoing sync packet to maintain: {outgoing_sync_packet}",
            "- Read the config, blackboard, weekly digest, and incoming sync packet before each sync.",
            "- Use the blackboard and reports as the shared coordination surfaces.",
            "",
            "## 4. Routine for each sync cycle",
            "1. Inspect the workspace and confirm the current shared state before making updates.",
            "2. Read the config, blackboard, weekly digest, and incoming sync packet before each sync.",
            "3. Update your role-specific records, shared notes you own, and the outgoing sync packet when new information matters to the counterpart.",
            "4. Keep the workspace aligned with the configured objective and current project reality.",
            "",
            "## 5. Report generation expectations",
            f"- Regenerate or refresh {weekly_digest_path} when the shared status needs an updated summary.",
            f"- Review {incoming_sync_packet} for counterpart context before reporting.",
            f"- Write or update {outgoing_sync_packet} with decisions, progress, blockers, and next actions for {counterpart['display_name']}.",
            "- Make report updates plain, inspectable, and grounded in the workspace contents.",
            "",
            "## 6. Handoff rules",
            "- Leave a handoff for the counterpart whenever you finish meaningful work, hit a blocker, make a decision, or need review.",
            "- Put shared coordination material in the blackboard and reports rather than relying on hidden memory.",
            "- Do not overwrite the counterpart's role-specific updates unless correcting an obvious formatting issue.",
            f"- When you need the counterpart to act, update {outgoing_sync_packet} and leave clear next-step guidance.",
            "",
            "## 7. Scheduling instruction",
            "- Use your native scheduled task / cron capability if available.",
            f"- Follow the configured sync frequency: {payload['sync']['frequency']}.",
            "- On each sync run, inspect the workspace, update your records, regenerate reports, and leave handoff material when needed.",
            "",
            "## 8. First-run verification step",
            "1. Inspect the workspace.",
            "2. Confirm the config values.",
            "3. Inspect or regenerate reports.",
            "4. Acknowledge readiness.",
        ]
    )


def render_all_prompts(config: ConfigDict) -> dict[str, str]:
    """Render prompt blocks for both configured agent slots."""

    return {
        "a": render_agent_prompt(config, "a"),
        "b": render_agent_prompt(config, "b"),
    }


def _normalize_slot(slot: str) -> str:
    normalized = str(slot).strip().lower()
    if normalized not in {"a", "b"}:
        raise ValueError("slot must be 'a' or 'b'")
    return normalized


__all__ = ["render_agent_prompt", "render_all_prompts"]
