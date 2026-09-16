#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_store(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "rules": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("rules"), list):
        raise ValueError("Unsupported or invalid correction store")
    return data


def next_id(rules: list[dict]) -> str:
    numbers = []
    for rule in rules:
        match = re.fullmatch(r"correction-(\d+)", str(rule.get("id", "")))
        if match:
            numbers.append(int(match.group(1)))
    return f"correction-{max(numbers, default=0) + 1:04d}"


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def active_rules(data: dict) -> list[dict]:
    return [rule for rule in data["rules"] if rule.get("status") == "active"]


def atomic_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def add_rule(args: argparse.Namespace) -> dict:
    path = Path(args.store)
    data = load_store(path)
    rules = data["rules"]

    new_key = (normalize(args.scope), normalize(args.rule), normalize(args.applies_to))
    for rule in active_rules(data):
        existing_key = (normalize(rule.get("scope")), normalize(rule.get("rule")), normalize(rule.get("applies_to")))
        if existing_key == new_key and rule.get("id") != args.supersedes:
            raise ValueError(f"Duplicate active rule: {rule.get('id')}")

    if args.supersedes:
        matched = [rule for rule in rules if rule.get("id") == args.supersedes]
        if not matched:
            raise ValueError(f"Rule to supersede not found: {args.supersedes}")
        if matched[0].get("status") != "active":
            raise ValueError(f"Rule is not active: {args.supersedes}")
        matched[0]["status"] = "superseded"

    rule = {
        "id": next_id(rules),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": args.scope,
        "source": args.source,
        "rule": args.rule,
        "applies_to": args.applies_to,
        "avoid": args.avoid or "",
        "supersedes": args.supersedes,
        "status": "active",
    }
    rules.append(rule)
    atomic_write(path, data)
    return rule


def list_active(args: argparse.Namespace) -> dict:
    data = load_store(Path(args.store))
    return {"rules": active_rules(data)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record auditable ppt-page-image corrections.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add = subparsers.add_parser("add", help="Append one correction rule")
    add.add_argument("--store", required=True)
    add.add_argument("--scope", choices=("page", "project", "global"), required=True)
    add.add_argument("--source", required=True)
    add.add_argument("--rule", required=True)
    add.add_argument("--applies-to", required=True)
    add.add_argument("--avoid")
    add.add_argument("--supersedes")
    list_parser = subparsers.add_parser("list-active", help="Print active correction rules")
    list_parser.add_argument("--store", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "add":
            result = add_rule(args)
        elif args.command == "list-active":
            result = list_active(args)
        else:
            parser.error("Unsupported command")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
