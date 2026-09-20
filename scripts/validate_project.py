#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from planning_documents import PLANNING_FILES, render_documents


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
STATUS_ORDER = {
    "INTAKE": 0,
    "STYLE_SAMPLING": 1,
    "STYLE_SELECTED": 2,
    "PLANNING_READY": 3,
    "PILOT_REVIEW": 4,
    "PILOT_APPROVED": 5,
    "FULL_PRODUCTION": 6,
    "QA": 7,
    "PDF_RENDER_CHECK": 8,
    "DELIVERY_READY": 9,
}
GATE_STATUS = {
    "planning": "PLANNING_READY",
    "pilot": "PILOT_APPROVED",
    "production": "FULL_PRODUCTION",
    "delivery": "DELIVERY_READY",
}
FONT_SUFFIXES = {".ttf", ".otf", ".ttc"}
QA_STATUSES = {"PENDING", "REVIEWED", "PASS", "FAIL"}


def require_nonempty_text(path: Path) -> None:
    if not path.is_file() or not path.read_text(encoding="utf-8").strip():
        raise ValueError(f"Required planning file is missing or empty: {path.name}")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_text(mapping: dict, key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be nonempty text")
    return value.strip()


def workspace_file(workspace: Path, relative: str, context: str) -> Path:
    candidate = (workspace / relative).resolve()
    root = workspace.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"{context} must stay inside workspace")
    return candidate


def validate_planning_documents(data: dict, workspace: Path) -> None:
    expected = render_documents(data)
    planning_dir = workspace / "planning"
    for filename, content in expected.items():
        path = planning_dir / filename
        if not path.is_file():
            raise ValueError(f"Required planning file is missing: {filename}")
        actual = path.read_text(encoding="utf-8")
        if actual != content:
            raise ValueError(f"Planning file drift: {filename}; regenerate it from project-state.json")


def validate_v2_structure(data: dict, workspace: Path) -> tuple[list[dict], dict, list[str]]:
    deck = data.get("deck")
    if not isinstance(deck, dict):
        raise ValueError("deck must be an object")
    for key in ("name", "audience", "scenario", "language", "source_authority", "content_scope"):
        require_text(deck, key, "deck")
    expected_pages = deck.get("expected_pages")
    if not isinstance(expected_pages, int) or expected_pages < 1:
        raise ValueError("deck.expected_pages must be a positive integer")
    if not isinstance(deck.get("assumptions"), list):
        raise ValueError("deck.assumptions must be a list")

    style = data.get("style")
    if not isinstance(style, dict):
        raise ValueError("style must be an object")
    for key in (
        "summary",
        "user_feedback",
        "fingerprint",
        "material",
        "image_treatment",
        "whitespace",
        "decoration_density",
        "typography_direction",
        "global_prompt",
    ):
        require_text(style, key, "style")
    for key in ("useful_traits", "rejected_traits", "permitted_variation", "global_negatives"):
        if not isinstance(style.get(key), list):
            raise ValueError(f"style.{key} must be a list")
    if not isinstance(style.get("palette_roles"), dict) or not style["palette_roles"]:
        raise ValueError("style.palette_roles must be a nonempty object")

    fonts = data.get("fonts")
    if not isinstance(fonts, list) or not fonts:
        raise ValueError("At least one font role is required")
    if len(fonts) > 7:
        raise ValueError(f"No more than 7 font roles are allowed; found {len(fonts)}")
    font_roles = []
    for index, font in enumerate(fonts, start=1):
        if not isinstance(font, dict):
            raise ValueError(f"Font {index} must be an object")
        role = require_text(font, "role", f"font {index}")
        for key in (
            "display_name",
            "weight",
            "source_path",
            "packaged_filename",
            "fallback",
            "visual_traits",
            "license_status",
        ):
            require_text(font, key, f"font {role}")
        packaged = font["packaged_filename"].strip()
        if Path(packaged).name != packaged or Path(packaged).suffix.lower() not in FONT_SUFFIXES:
            raise ValueError(f"Font {role} has invalid packaged_filename: {packaged}")
        if not (workspace / "fonts" / packaged).is_file():
            raise ValueError(f"Packaged font file is missing: {packaged}")
        font_roles.append(role)
    if len(font_roles) != len(set(font_roles)):
        raise ValueError("Font roles must be unique")

    families = data.get("families")
    if not isinstance(families, dict) or not families:
        raise ValueError("At least one page family is required")
    assigned_pages = []
    for name, family in families.items():
        if not isinstance(family, dict):
            raise ValueError(f"Family {name} must be an object")
        family_pages = family.get("pages")
        if not isinstance(family_pages, list) or not family_pages or family.get("mother_page") not in family_pages:
            raise ValueError(f"Family {name} must list pages and a mother_page within that list")
        if not isinstance(family.get("invariants"), list) or not family["invariants"]:
            raise ValueError(f"Family {name} must define at least one invariant")
        if len(family_pages) > 1:
            specifications = family.get("component_specifications")
            if not isinstance(specifications, list) or not specifications:
                raise ValueError(f"Repeated family {name} must define component_specifications")
            for spec_index, specification in enumerate(specifications, start=1):
                if not isinstance(specification, dict):
                    raise ValueError(f"Family {name} component specification {spec_index} must be an object")
                require_text(specification, "name", f"family {name} specification {spec_index}")
                if sorted(specification.get("applies_to") or []) != sorted(family_pages):
                    raise ValueError(
                        f"Family {name} component specification {spec_index} applies_to must match family pages"
                    )
                for field in ("fixed", "variable", "forbidden"):
                    value = specification.get(field)
                    if not isinstance(value, list) or not value:
                        raise ValueError(
                            f"Family {name} component specification {spec_index} requires nonempty {field}"
                        )
        assigned_pages.extend(family_pages)

    pages = data.get("pages")
    if not isinstance(pages, list) or len(pages) != expected_pages:
        raise ValueError(f"Project page count mismatch: found {len(pages or [])}, expected {expected_pages}")
    indices = [page.get("index") for page in pages]
    if indices != list(range(1, expected_pages + 1)):
        raise ValueError(f"Page indices must be continuous from 1: {indices}")
    if sorted(assigned_pages) != indices:
        raise ValueError("Every page must belong to exactly one page family")

    known_roles = set(font_roles)
    required_page_text = (
        "type",
        "goal",
        "title",
        "design_rationale",
        "family",
        "density_risk",
        "visual_subject",
        "image_text_relationship",
        "prompt",
    )
    for page in pages:
        index = page["index"]
        for key in required_page_text:
            require_text(page, key, f"page {index}")
        if page["family"] not in families:
            raise ValueError(f"Page {index} uses unknown family: {page['family']}")
        if index not in families[page["family"]].get("pages", []):
            raise ValueError(f"Page {index} has inconsistent family assignment: {page['family']}")
        visible_copy = page.get("visible_copy")
        if not isinstance(visible_copy, list) or not visible_copy:
            raise ValueError(f"Page {index} must define visible_copy as a nonempty list")
        if any(not isinstance(item, str) or not item.strip() for item in visible_copy):
            raise ValueError(f"Page {index} contains an empty locked copy item")
        prompt = page["prompt"]
        missing_copy = [item for item in visible_copy if item not in prompt]
        if missing_copy:
            raise ValueError(f"Page {index} prompt is missing locked copy: {missing_copy}")
        roles = page.get("font_roles")
        if not isinstance(roles, list) or not roles:
            raise ValueError(f"Page {index} must use at least one font role")
        unknown_roles = sorted(set(roles) - known_roles)
        if unknown_roles:
            raise ValueError(f"Page {index} uses unknown font roles: {unknown_roles}")
        missing_roles = [role for role in roles if role not in prompt]
        if missing_roles:
            raise ValueError(f"Page {index} prompt is missing font role: {missing_roles}")
        for key in ("required_facts", "source_notes", "content_evidence", "reading_order", "negative_constraints"):
            if not isinstance(page.get(key), list):
                raise ValueError(f"Page {index}.{key} must be a list")
        if not isinstance(page.get("element_budget"), dict) or not isinstance(page.get("zones"), dict):
            raise ValueError(f"Page {index} must define element_budget and zones")
        if page.get("qa_status") not in QA_STATUSES:
            raise ValueError(f"Page {index} has invalid qa_status: {page.get('qa_status')}")
        if not isinstance(page.get("defects"), list):
            raise ValueError(f"Page {index}.defects must be a list")

    enrichment = data.get("enrichment")
    if not isinstance(enrichment, list):
        raise ValueError("enrichment must be a list")
    for item_index, item in enumerate(enrichment, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Enrichment item {item_index} must be an object")
        status = item.get("status")
        if status not in {"accepted", "rejected"}:
            raise ValueError(f"Enrichment item {item_index} has invalid status: {status}")
        if status == "rejected":
            if not isinstance(item.get("rejection_reason"), str) or not item["rejection_reason"].strip():
                raise ValueError(f"Rejected enrichment item {item_index} lacks rejection_reason")
            continue
        required = ("type", "teaching_purpose", "source", "verified_date", "rights_status", "target_pages")
        missing = [field for field in required if not item.get(field)]
        if missing:
            raise ValueError(f"Accepted enrichment item {item_index} lacks: {', '.join(missing)}")
        targets = item["target_pages"]
        if not isinstance(targets, list) or not targets or any(page not in indices for page in targets):
            raise ValueError(f"Enrichment item {item_index} has invalid target_pages")
        if item.get("type") == "authentic_photo" and not item.get("fidelity_constraints"):
            raise ValueError(f"Authentic photo item {item_index} lacks fidelity_constraints")
    if not isinstance(data.get("reviews"), dict):
        raise ValueError("reviews must be an object")
    delivery = data.get("delivery")
    if not isinstance(delivery, dict):
        raise ValueError("delivery must be an object")
    require_text(delivery, "deck_name", "delivery")
    if not isinstance(delivery.get("images"), list):
        raise ValueError("delivery.images must be a list")
    return pages, families, font_roles


def validate_gate_status(data: dict, gate: str) -> None:
    status = data.get("status")
    if status not in STATUS_ORDER:
        raise ValueError(f"Invalid project status: {status}")
    required = GATE_STATUS[gate]
    if STATUS_ORDER[status] < STATUS_ORDER[required]:
        raise ValueError(f"{gate} gate requires status {required} or later; found {status}")


def validate_pilot_evidence(data: dict, project_pages: list[dict]) -> None:
    review = (data.get("reviews") or {}).get("pilot") or {}
    pages = review.get("pages")
    reviewed = review.get("reviewed_pages")
    if review.get("status") != "pass" or not isinstance(pages, list) or not pages or sorted(pages) != sorted(reviewed or []):
        raise ValueError("pilot review evidence must be pass with matching nonempty pages and reviewed_pages")
    valid_pages = {page["index"] for page in project_pages}
    invalid = sorted(set(pages) - valid_pages)
    if invalid:
        raise ValueError(f"pilot review contains invalid page numbers: {invalid}")


def validate_production_evidence(pages: list[dict], workspace: Path) -> None:
    for page in pages:
        index = page["index"]
        if page.get("qa_status") not in {"PASS", "REVIEWED"}:
            raise ValueError(f"Page {index} must pass QA before production gate")
        relative = page.get("current_image")
        if not isinstance(relative, str) or not relative.strip():
            raise ValueError(f"Page {index} lacks current_image")
        image = workspace_file(workspace, relative, f"Page {index} current_image")
        if not image.is_file():
            raise ValueError(f"Page {index} current_image not found: {relative}")
        digest = page.get("image_sha256")
        if digest != file_sha256(image):
            raise ValueError(f"Page {index} image_sha256 does not match current_image")


def validate_delivery_evidence(data: dict, pages: list[dict], families: dict) -> None:
    for page in pages:
        if page.get("qa_status") != "PASS":
            raise ValueError(f"Page {page['index']} must be PASS for delivery gate")
    reviews = data["reviews"]
    family_reviews = reviews.get("families") or {}
    for name, family in families.items():
        if len(family.get("pages") or []) < 2:
            continue
        review = family_reviews.get(name) or {}
        if review.get("status") != "pass":
            raise ValueError(f"Family {name} review must pass for delivery gate")
        member_hashes = review.get("member_hashes") or {}
        expected = {str(page["index"]): page.get("image_sha256") for page in pages if page["family"] == name}
        if member_hashes != expected:
            raise ValueError(f"Family {name} review hashes do not match current pages")
    if (reviews.get("deck") or {}).get("status") != "pass":
        raise ValueError("whole-deck review must pass for delivery gate")
    if (reviews.get("render") or {}).get("status") != "pass":
        raise ValueError("render review must pass for delivery gate")


def validate_v2(state_path: Path, workspace: Path, gate: str) -> dict:
    if gate not in GATE_STATUS:
        raise ValueError(f"Unsupported gate: {gate}")
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise ValueError("validate_v2 requires project-state schema_version 2")
    validate_gate_status(data, gate)
    pages, families, font_roles = validate_v2_structure(data, workspace)
    validate_planning_documents(data, workspace)
    if gate in {"pilot", "production", "delivery"}:
        validate_pilot_evidence(data, pages)
    if gate in {"production", "delivery"}:
        validate_production_evidence(pages, workspace)
    if gate == "delivery":
        validate_delivery_evidence(data, pages, families)
    return {
        "deck": data["deck"]["name"],
        "schema_version": 2,
        "legacy": False,
        "status": data["status"],
        "gate": gate,
        "pages": len(pages),
        "families": len(families),
        "font_roles": len(font_roles),
    }


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
        packaged_filename = str(font.get("packaged_filename") or "").strip()
        if not packaged_filename:
            raise ValueError(f"Font role lacks packaged_filename: {font.get('role')}")
        if not (project_dir / "fonts" / packaged_filename).is_file():
            raise ValueError(f"Packaged font file is missing: {packaged_filename}")

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
        if len(family_pages) > 1:
            specifications = family.get("component_specifications")
            if not isinstance(specifications, list) or not specifications:
                raise ValueError(f"Repeated family {name} must define component_specifications")
            for spec_index, specification in enumerate(specifications, start=1):
                if not str(specification.get("name") or "").strip():
                    raise ValueError(f"Family {name} component specification {spec_index} lacks name")
                if sorted(specification.get("applies_to") or []) != sorted(family_pages):
                    raise ValueError(
                        f"Family {name} component specification {spec_index} applies_to must match family pages"
                    )
                for field in ("fixed", "variable", "forbidden"):
                    value = specification.get(field)
                    if not isinstance(value, list) or not value:
                        raise ValueError(
                            f"Family {name} component specification {spec_index} requires nonempty {field}"
                        )
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
        "schema_version": 1,
        "legacy": True,
        "status": data["status"],
        "pages": expected_pages,
        "families": len(families),
        "font_roles": len(fonts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ppt-page-image planning state.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--project-dir")
    parser.add_argument("--workspace")
    parser.add_argument("--gate", choices=tuple(GATE_STATUS), default="planning")
    args = parser.parse_args()
    try:
        state_path = Path(args.state)
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if data.get("schema_version") == 2:
            if not args.workspace:
                raise ValueError("--workspace is required for schema_version 2")
            result = validate_v2(state_path, Path(args.workspace), args.gate)
        else:
            if not args.project_dir:
                raise ValueError("--project-dir is required for schema_version 1")
            result = validate(state_path, Path(args.project_dir))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
