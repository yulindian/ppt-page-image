#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path

from planning_documents import write_documents


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ppt-page-image planning documents from schema-v2 state.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    try:
        state = json.loads(Path(args.state).read_text(encoding="utf-8"))
        outputs = write_documents(state, Path(args.out_dir))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "outputs": {
                    name: {"path": str(path), "sha256": file_sha256(path)}
                    for name, path in outputs.items()
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
