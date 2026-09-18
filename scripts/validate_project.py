#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


PLANNING_FILES = ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt")
STATUSES = {
    "INTAKE",
    "STYLE_SAMPLING",
    "STYLE_SELECTED",
    "PLANNING_READY",
    "PILOT_REVIEW",
    "PILOT_APPROVED",
    "FULL_PRODUCTION",
    "QA",
    "PDF_RENDER_CHECK",
    "DELIVERY_READY",
}


def require_nonempty_text(path: Path) -> None:
    if not path.is_file() or not path.read_text(encoding="utf-8").strip():
        raise ValueError(f"Required planning file is missing or empty: {path.name}")


def validate(state_path: Path, project_dir: Path) -> dict:
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported project-state schema")
    if data.get("status") not in STATUSES:
        raise ValueError(f"Invalid project status: {data.get('status')}")

    for filename in PLANNING_FILES:
        require_nonempty_text(project_dir / filename)

    deck = data.get("deck") or {}
    expected_pages = deck.get("expected_pages")
    if not isinstance(deck.get("name"), str) or not deck["name"].strip():
        raise ValueError("deck.name is required")
    if not isinstance(expected_pages, int) or expected_pages < 1:
        raise ValueError("deck.expected_pages must be a positive integer")

    pages = data.get("pages")
    if not isinstance(pages, list) or len(pages) != expected_pages:
        raise ValueError(f"Project page count mismatch: found {len(pages or [])}, expected {expected_pages}")
    indices = [page.get("index") for page in pages]
    if indices != list(range(1, expected_pages + 1)):
        raise ValueError(f"Page indices must be continuous from 1: {indices}")

    fonts = data.get("fonts")
    if not isinstance(fonts, list) or not fonts:
        raise ValueError("At least one font role is required")
    if len(fonts) > 7:
        raise ValueError(f"No more than 7 font roles are allowed; found {len(fonts)}")
    font_roles = [font.get("role") for font in fonts]
    if len(set(font_roles)) != len(font_roles) or any(not role for role in font_roles):
        raise ValueError("Font roles must be nonempty and unique")
    for font in fonts:
        if not str(font.get("packaged_filename") or "").strip():
            raise ValueError(f"Font role lacks packaged_filename: {font.get('role')}")

    families = data.get("families")
    if not isinstance(families, dict) or not families:
        raise ValueError("At least one page family is required")
    assigned_pages = []
    for name, family in families.items():
        family_pages = family.get("pages") or []
        if not family_pages or family.get("mother_page") not in family_pages:
            raise ValueError(f"Family {name} must list pages and a mother_page within that list")
        if not family.get("invariants"):
            raise ValueError(f"Family {name} must define at least one invariant")
        assigned_pages.extend(family_pages)
    if sorted(assigned_pages) != list(range(1, expected_pages + 1)):
        raise ValueError("Every page must belong to exactly one page family")

    enrichment = data.get("enrichment") or []
    if not isinstance(enrichment, list):
        raise ValueError("enrichment must be a list when present")
    for item_index, item in enumerate(enrichment, start=1):
        status = item.get("status")
        if status not in {"accepted", "rejected"}:
            raise ValueError(f"Enrichment item {item_index} has invalid status: {status}")
        if status == "rejected":
            if not str(item.get("rejection_reason") or "").strip():
                raise ValueError(f"Rejected enrichment item {item_index} lacks rejection_reason")
            continue
        required = ("type", "teaching_purpose", "source", "verified_date", "rights_status", "target_pages")
        missing = [field for field in required if not item.get(field)]
        if missing:
            raise ValueError(f"Accepted enrichment item {item_index} lacks: {', '.join(missing)}")
        targets = item["target_pages"]
        if not isinstance(targets, list) or any(page not in range(1, expected_pages + 1) for page in targets):
            raise ValueError(f"Enrichment item {item_index} has invalid target_pages")
        if item.get("type") == "authentic_photo" and not item.get("fidelity_constraints"):
            raise ValueError(f"Authentic photo item {item_index} lacks fidelity_constraints")

    known_roles = set(font_roles)
    for page in pages:
        index = page["index"]
        title = str(page.get("title") or "").strip()
        family = page.get("family")
        visible_copy = page.get("visible_copy")
        prompt = str(page.get("prompt") or "")
        roles = page.get("font_roles") or []
        if not title:
            raise ValueError(f"Page {index} lacks title")
        if family not in families or index not in families[family].get("pages", []):
            raise ValueError(f"Page {index} has inconsistent family assignment: {family}")
        if not isinstance(visible_copy, list) or not visible_copy:
            raise ValueError(f"Page {index} must define visible_copy as a nonempty list")
        missing_copy = [str(item) for item in visible_copy if str(item) not in prompt]
        if missing_copy:
            raise ValueError(f"Page {index} prompt is missing locked copy: {missing_copy}")
        unknown_roles = sorted(set(roles) - known_roles)
        if unknown_roles:
            raise ValueError(f"Page {index} uses unknown font roles: {unknown_roles}")
        if not prompt.strip():
            raise ValueError(f"Page {index} lacks a generation prompt")

    return {
        "deck": deck["name"],
        "status": data["status"],
        "pages": expected_pages,
        "families": len(families),
        "font_roles": len(fonts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ppt-page-image planning state.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--project-dir", required=True)
    args = parser.parse_args()
    try:
        result = validate(Path(args.state), Path(args.project_dir))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
