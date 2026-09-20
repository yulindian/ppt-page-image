#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_delivery
from planning_documents import PLANNING_FILES
from validate_project import validate_v2, workspace_file


def _move_path(source: Path, target: Path) -> None:
    source.replace(target)


def _managed_root_names(deck_name: str) -> set[str]:
    return {f"{deck_name}.pdf", *PLANNING_FILES, "fonts", "images"}


def _ensure_separate_paths(workspace: Path, delivery_dir: Path) -> None:
    workspace_root = workspace.resolve()
    delivery_root = delivery_dir.resolve()
    if (
        workspace_root == delivery_root
        or delivery_root.is_relative_to(workspace_root)
        or workspace_root.is_relative_to(delivery_root)
    ):
        raise ValueError("Workspace and final delivery must be separate, non-nested directories")


def _ensure_existing_target_is_managed(delivery_dir: Path, deck_name: str) -> None:
    if not delivery_dir.exists():
        return
    if not delivery_dir.is_dir():
        raise ValueError(f"Delivery target is not a directory: {delivery_dir}")
    allowed = _managed_root_names(deck_name)
    unmanaged = sorted(path.name for path in delivery_dir.iterdir() if path.name not in allowed)
    process = sorted(
        str(path.relative_to(delivery_dir))
        for path in delivery_dir.rglob("*")
        if validate_delivery.has_stale_or_process_name(path)
    )
    if unmanaged or process:
        details = unmanaged + process
        raise ValueError(f"Existing delivery contains unmanaged items: {', '.join(details)}")


def _copy_registered_fonts(state: dict, workspace: Path, staging: Path) -> None:
    destination = staging / "fonts"
    destination.mkdir()
    for font in state["fonts"]:
        filename = font["packaged_filename"]
        source = workspace / "fonts" / filename
        shutil.copy2(source, destination / filename)


def _copy_registered_images(state: dict, workspace: Path, staging: Path) -> None:
    entries = state["delivery"].get("images") or []
    if not entries:
        return
    destination = staging / "images"
    destination.mkdir()
    for index, entry in enumerate(entries, start=1):
        if isinstance(entry, str):
            relative = f"images/{entry}"
            filename = entry
        elif isinstance(entry, dict):
            relative = entry.get("workspace_path") or f"images/{entry.get('filename', '')}"
            filename = entry.get("filename") or Path(relative).name
        else:
            raise ValueError(f"delivery.images item {index} must be text or an object")
        if not filename or Path(filename).name != filename:
            raise ValueError(f"delivery.images item {index} has invalid filename")
        source = workspace_file(workspace, str(relative), f"delivery.images item {index}")
        if not source.is_file():
            raise ValueError(f"Registered delivery image not found: {relative}")
        shutil.copy2(source, destination / filename)


def _build_staging(state: dict, workspace: Path, pdf_path: Path, staging: Path) -> None:
    deck_name = state["delivery"]["deck_name"]
    shutil.copy2(pdf_path, staging / f"{deck_name}.pdf")
    for filename in PLANNING_FILES:
        shutil.copy2(workspace / "planning" / filename, staging / filename)
    _copy_registered_fonts(state, workspace, staging)
    _copy_registered_images(state, workspace, staging)


def promote(
    state_path: Path,
    workspace: Path,
    pdf_path: Path,
    delivery_dir: Path,
    render_report: Path,
) -> dict:
    _ensure_separate_paths(workspace, delivery_dir)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    validate_v2(state_path, workspace, "delivery")
    if not pdf_path.is_file():
        raise ValueError(f"Candidate PDF not found: {pdf_path}")
    deck_name = state["delivery"]["deck_name"]
    _ensure_existing_target_is_managed(delivery_dir, deck_name)
    delivery_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{delivery_dir.name}.staging-", dir=delivery_dir.parent))
    previous = None
    try:
        _build_staging(state, workspace, pdf_path, staging)
        validation = validate_delivery.validate(
            staging,
            deck_name,
            state["deck"]["expected_pages"],
            render_report,
        )
        if delivery_dir.exists():
            history = workspace / "history"
            history.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            previous = history / f"delivery-{stamp}"
            _move_path(delivery_dir, previous)
        try:
            _move_path(staging, delivery_dir)
        except Exception:
            if previous is not None and previous.exists() and not delivery_dir.exists():
                _move_path(previous, delivery_dir)
            raise
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {
        "delivery": str(delivery_dir),
        "previous_delivery": str(previous) if previous is not None else None,
        "validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote a clean ppt-page-image delivery from an external workspace.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--delivery-dir", required=True)
    parser.add_argument("--render-report", required=True)
    args = parser.parse_args()
    try:
        result = promote(
            Path(args.state),
            Path(args.workspace),
            Path(args.pdf),
            Path(args.delivery_dir),
            Path(args.render_report),
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
