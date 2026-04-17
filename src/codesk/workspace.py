"""Workspace initialization for CoDesk."""

from pathlib import Path


WORKSPACE_ROOT_NAME = "assistant-sync"
EXPECTED_WORKSPACE_DIRS = (
    Path("."),
    Path("blackboard"),
    Path("blackboard/projects"),
    Path("blackboard/weekly"),
    Path("blackboard/handoffs"),
    Path("blackboard/decisions"),
    Path("hermes_to_openclaw"),
    Path("openclaw_to_hermes"),
    Path("shared"),
    Path("shared/reports"),
    Path("references"),
    Path("references/source-pointers"),
)


def init_workspace(target_dir: str | Path) -> Path:
    """Create the CoDesk workspace tree under ``target_dir``."""

    workspace_root = Path(target_dir).expanduser() / WORKSPACE_ROOT_NAME

    for relative_path in EXPECTED_WORKSPACE_DIRS:
        (workspace_root / relative_path).mkdir(parents=True, exist_ok=True)

    return workspace_root
