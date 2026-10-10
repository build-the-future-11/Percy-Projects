from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .ledger import BusyError, GateError, IntegrityError, Project, strict_json


def load(path):
    return strict_json(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Record and verify research state and evidence; never execute scientific jobs.")
    subs = parser.add_subparsers(dest="command", required=True)

    def command(name, help_text):
        sub = subs.add_parser(name, help=help_text)
        sub.add_argument("project", help="Project directory containing canonical STATE.md")
        return sub

    sub = command("init", "Initialize a new canonical project contract")
    sub.add_argument("--contract", required=True)
    sub = command("artifact", "Snapshot and hash one retained artifact")
    sub.add_argument("--id", required=True)
    sub.add_argument("--kind", required=True)
    sub.add_argument("--file", required=True)
    sub.add_argument("--parents", nargs="*", default=[])
    sub.add_argument("--expected-head")
    sub = command("checkpoint", "Record reviewer qualification for checkpoint 1 through 6")
    sub.add_argument("--number", type=int, required=True)
    sub.add_argument("--evidence", required=True)
    sub.add_argument("--reviewer", required=True)
    sub.add_argument("--note", required=True)
    sub.add_argument("--expected-head")
    for name, field in (("freeze", "protocol_artifact"), ("verify-review", "verification_artifact"), ("complete", "release_artifact")):
        sub = command(name, f"Advance the {name} gate")
        sub.add_argument("--artifact", required=True, dest=field)
        sub.add_argument("--expected-head")
    for name in ("run", "claim", "note", "revise", "lock-evidence", "close-invalid"):
        sub = command(name, f"Record a {name} JSON receipt")
        sub.add_argument("--json", required=True)
        sub.add_argument("--expected-head")
    for name in ("state", "verify", "history"):
        sub = command(name, f"Read and verify project {name}")
        sub.add_argument("--expected-head")
    for name in ("successor", "correct-invalid"):
        sub = command(name, "Create a separate study without editing its terminal predecessor")
        sub.add_argument("--target", required=True)
        sub.add_argument("--contract", required=True)
        sub.add_argument("--relationship", required=True)
        sub.add_argument("--protocol", required=True)
    args = parser.parse_args(argv)
    project = Project(args.project)
    try:
        if args.command == "init":
            result = project.initialize(load(args.contract))
        elif args.command == "artifact":
            result = project.add_artifact(args.id, args.kind, args.file, args.parents, expected_head=args.expected_head)
        elif args.command == "checkpoint":
            result = project.apply("checkpoint", {"number": args.number, "evidence": args.evidence, "reviewer": args.reviewer, "note": args.note}, expected_head=args.expected_head)
        elif args.command in {"freeze", "verify-review", "complete"}:
            field = {"freeze": "protocol_artifact", "verify-review": "verification_artifact", "complete": "release_artifact"}[args.command]
            result = project.apply(args.command.replace("-", "_"), {field: getattr(args, field)}, expected_head=args.expected_head)
        elif args.command in {"run", "claim", "note", "revise", "lock-evidence", "close-invalid"}:
            result = project.apply(args.command.replace("-", "_"), load(args.json), expected_head=args.expected_head)
        elif args.command in {"successor", "correct-invalid"}:
            result = project.successor(args.target, load(args.contract), load(args.relationship), args.protocol,
                                       validity_correction=args.command == "correct-invalid")
        elif args.command == "history":
            result = project.history(expected_head=args.expected_head)
        else:
            result = project.read(expected_head=args.expected_head)
            if args.command == "verify":
                result = {"valid": True, "head": result["head"], "event_count": result["event_count"], "artifact_count": len(result["state"]["artifacts"])}
    except (GateError, IntegrityError, BusyError, OSError, UnicodeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
