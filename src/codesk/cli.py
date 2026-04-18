"""Command line interface for CoDesk."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from codesk.bootstrap import SetupRequest, run_setup
from codesk.config import CONFIG_FILE_NAME, load_config, summarize_config
from codesk.digest import build_weekly_digest_markdown, write_weekly_digest_report
from codesk.indexing import build_status_summary
from codesk.prompts import render_all_prompts
from codesk.sync_packet import build_sync_packet_markdown, write_sync_packet_report
from codesk.templates import (
    create_decision_record,
    create_handoff_record,
    create_project_record,
    create_weekly_record,
)
from codesk.validation import validate_workspace
from codesk.workspace import WORKSPACE_ROOT_NAME, init_workspace


def _workspace_root(directory: str | Path) -> Path:
    return init_workspace(directory)


def _config_path_from_directory(directory: str | Path) -> Path:
    target = Path(directory).expanduser()

    if target.is_file() and target.name == CONFIG_FILE_NAME:
        return target

    workspace_config = target / CONFIG_FILE_NAME
    if workspace_config.is_file():
        return workspace_config

    nested_workspace_config = target / WORKSPACE_ROOT_NAME / CONFIG_FILE_NAME
    if nested_workspace_config.is_file():
        return nested_workspace_config

    return nested_workspace_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codesk",
        description="Initialize and manage a CoDesk collaboration workspace.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init",
        help="Create the assistant-sync workspace tree.",
    )
    init_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory for the workspace root.",
    )

    setup = subparsers.add_parser(
        "setup",
        help="Create a ready-to-use CoDesk workspace, config, and prompts.",
    )
    setup.add_argument("directory", nargs="?", default=".")
    setup.add_argument("--project-name")
    setup.add_argument("--objective")
    setup.add_argument("--agent-a")
    setup.add_argument("--agent-b")
    setup.add_argument("--sync-frequency")
    setup.add_argument("--notes")
    setup.add_argument("--seed-project-id")
    setup.add_argument("--agent-a-home")
    setup.add_argument("--agent-b-home")

    print_prompts = subparsers.add_parser(
        "print-prompts",
        help="Print both bootstrap prompt blocks from an existing config.",
    )
    print_prompts.add_argument("directory", nargs="?", default=".")

    show_config = subparsers.add_parser(
        "show-config",
        help="Show a human-readable summary from an existing config.",
    )
    show_config.add_argument("directory", nargs="?", default=".")

    new_project = subparsers.add_parser("new-project", help="Create a project record.")
    new_project.add_argument("directory", nargs="?", default=".")
    new_project.add_argument("--project-id", required=True)
    new_project.add_argument("--title", required=True)
    new_project.add_argument("--owner", required=True)
    new_project.add_argument("--status", required=True)

    new_weekly = subparsers.add_parser("new-weekly", help="Create a weekly sync record.")
    new_weekly.add_argument("directory", nargs="?", default=".")
    new_weekly.add_argument("--week", required=True)
    new_weekly.add_argument("--assistant", required=True)
    new_weekly.add_argument("--completed", default="TBD")
    new_weekly.add_argument("--in-progress", dest="in_progress", default="TBD")
    new_weekly.add_argument("--blockers", default="TBD")
    new_weekly.add_argument(
        "--needs-from-counterpart",
        dest="needs_from_counterpart",
        default="TBD",
    )
    new_weekly.add_argument("--source-pointers", dest="source_pointers", default="TBD")

    new_handoff = subparsers.add_parser("new-handoff", help="Create a handoff record.")
    new_handoff.add_argument("directory", nargs="?", default=".")
    new_handoff.add_argument("--handoff-id", required=True)
    new_handoff.add_argument("--from-assistant", required=True)
    new_handoff.add_argument("--to-assistant", required=True)
    new_handoff.add_argument("--project", required=True)
    new_handoff.add_argument("--context-summary", dest="context_summary", default="TBD")
    new_handoff.add_argument("--requested-action", dest="requested_action", default="TBD")
    new_handoff.add_argument("--priority", default="normal")
    new_handoff.add_argument("--due-hint", dest="due_hint", default="TBD")
    new_handoff.add_argument("--evidence", default="TBD")

    new_decision = subparsers.add_parser("new-decision", help="Create a decision record.")
    new_decision.add_argument("directory", nargs="?", default=".")
    new_decision.add_argument("--decision-id", required=True)
    new_decision.add_argument("--topic", required=True)

    validate = subparsers.add_parser("validate", help="Validate blackboard records.")
    validate.add_argument("directory", nargs="?", default=".")

    status = subparsers.add_parser("status", help="Show a compact blackboard summary.")
    status.add_argument("directory", nargs="?", default=".")

    weekly_digest = subparsers.add_parser(
        "weekly-digest",
        help="Render a markdown weekly digest for the shared blackboard.",
    )
    weekly_digest.add_argument("directory", nargs="?", default=".")
    weekly_digest.add_argument(
        "--write",
        action="store_true",
        help="Write the digest into shared/reports/weekly-digest.md.",
    )

    sync_packet = subparsers.add_parser(
        "sync-packet",
        help="Render a counterpart-ready sync packet.",
    )
    sync_packet.add_argument("directory", nargs="?", default=".")
    sync_packet.add_argument("--from-assistant", required=True)
    sync_packet.add_argument("--to-assistant", required=True)
    sync_packet.add_argument(
        "--write",
        action="store_true",
        help="Write the sync packet into shared/reports/.",
    )

    generate_reports = subparsers.add_parser(
        "generate-reports",
        help="Write the weekly digest and both sync-packet directions into shared/reports/.",
    )
    generate_reports.add_argument("directory", nargs="?", default=".")
    generate_reports.add_argument("--assistant-a", required=True)
    generate_reports.add_argument("--assistant-b", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        workspace_root = init_workspace(args.directory)
        print(f"Initialized CoDesk workspace at {workspace_root}")
        return 0

    if args.command == "setup":
        result = run_setup(
            SetupRequest(
                directory=args.directory,
                project_name=args.project_name,
                objective=args.objective,
                agent_a=args.agent_a,
                agent_b=args.agent_b,
                sync_frequency=args.sync_frequency,
                notes=args.notes,
                seed_project_id=args.seed_project_id,
                agent_a_home=args.agent_a_home,
                agent_b_home=args.agent_b_home,
            )
        )
        print("CoDesk workspace created at:")
        print(result.workspace_path)
        print()
        print("Config written to:")
        print(result.config_path)
        print()
        print("Next step:")
        print("1. Copy PROMPT A into Agent 1")
        print("2. Copy PROMPT B into Agent 2")
        print("3. Ask each agent to confirm its first sync run")
        print()
        print("===== PROMPT FOR AGENT 1 =====")
        print(result.prompt_a)
        print()
        print("===== PROMPT FOR AGENT 2 =====")
        print(result.prompt_b)
        return 0

    if args.command == "print-prompts":
        config = load_config(_config_path_from_directory(args.directory))
        prompts = render_all_prompts(config)
        print("===== PROMPT FOR AGENT 1 =====")
        print(prompts["a"])
        print()
        print("===== PROMPT FOR AGENT 2 =====")
        print(prompts["b"])
        return 0

    if args.command == "show-config":
        config = load_config(_config_path_from_directory(args.directory))
        print(summarize_config(config))
        return 0

    if args.command == "new-project":
        path = create_project_record(
            _workspace_root(args.directory),
            project_id=args.project_id,
            title=args.title,
            owner=args.owner,
            status=args.status,
        )
        print(f"Created project record at {path}")
        return 0

    if args.command == "new-weekly":
        path = create_weekly_record(
            _workspace_root(args.directory),
            week=args.week,
            assistant=args.assistant,
            completed=args.completed,
            in_progress=args.in_progress,
            blockers=args.blockers,
            needs_from_counterpart=args.needs_from_counterpart,
            source_pointers=args.source_pointers,
        )
        print(f"Created weekly record at {path}")
        return 0

    if args.command == "new-handoff":
        path = create_handoff_record(
            _workspace_root(args.directory),
            handoff_id=args.handoff_id,
            from_assistant=args.from_assistant,
            to_assistant=args.to_assistant,
            project=args.project,
            context_summary=args.context_summary,
            requested_action=args.requested_action,
            priority=args.priority,
            due_hint=args.due_hint,
            evidence=args.evidence,
        )
        print(f"Created handoff record at {path}")
        return 0

    if args.command == "new-decision":
        path = create_decision_record(
            _workspace_root(args.directory),
            decision_id=args.decision_id,
            topic=args.topic,
        )
        print(f"Created decision record at {path}")
        return 0

    if args.command == "validate":
        result = validate_workspace(_workspace_root(args.directory))
        if result["ok"]:
            print("Validation passed")
            return 0
        print(f"Validation failed with {result['error_count']} error(s)")
        for error in result["errors"]:
            print(f"{error['code']}: {error['path']} [{error['field']}]")
        return 1

    if args.command == "status":
        summary = build_status_summary(_workspace_root(args.directory))
        counts = summary["counts"]
        print(f"Projects: {counts['projects']}")
        print(f"Weekly: {counts['weekly']}")
        print(f"Handoffs: {counts['handoffs']}")
        print(f"Decisions: {counts['decisions']}")
        if summary["latest_projects"]:
            print("\nLatest project updates:")
            for project in summary["latest_projects"]:
                print(
                    f"- {project['project_id']} | {project['status']} | {project['owner']}"
                )
        if summary["recent_handoffs"]:
            print("\nRecent handoffs:")
            for handoff in summary["recent_handoffs"]:
                print(
                    f"- {handoff['handoff_id']} | {handoff['from']} -> {handoff['to']} | {handoff['project']}"
                )
        return 0

    if args.command == "weekly-digest":
        workspace_root = _workspace_root(args.directory)
        if args.write:
            path = write_weekly_digest_report(workspace_root)
            print(f"Wrote weekly digest report to {path}")
        else:
            print(build_weekly_digest_markdown(workspace_root), end="")
        return 0

    if args.command == "sync-packet":
        workspace_root = _workspace_root(args.directory)
        if args.write:
            path = write_sync_packet_report(
                workspace_root,
                from_assistant=args.from_assistant,
                to_assistant=args.to_assistant,
            )
            print(f"Wrote sync packet report to {path}")
        else:
            print(
                build_sync_packet_markdown(
                    workspace_root,
                    from_assistant=args.from_assistant,
                    to_assistant=args.to_assistant,
                ),
                end="",
            )
        return 0

    if args.command == "generate-reports":
        workspace_root = _workspace_root(args.directory)
        digest_path = write_weekly_digest_report(workspace_root)
        packet_ab = write_sync_packet_report(
            workspace_root,
            from_assistant=args.assistant_a,
            to_assistant=args.assistant_b,
        )
        packet_ba = write_sync_packet_report(
            workspace_root,
            from_assistant=args.assistant_b,
            to_assistant=args.assistant_a,
        )
        print(f"Wrote weekly digest report to {digest_path}")
        print(f"Wrote sync packet report to {packet_ab}")
        print(f"Wrote sync packet report to {packet_ba}")
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
