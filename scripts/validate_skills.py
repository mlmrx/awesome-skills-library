#!/usr/bin/env python3
"""Validate Awesome Skills Library skill packages without external dependencies."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REQUIRED_FILES = ["SKILL.md", "skill.yaml", "tests/basic.yaml"]
REQUIRED_FIELDS = [
    "id",
    "name",
    "version",
    "category",
    "description",
    "use_cases",
    "inputs",
    "outputs",
    "required_tools",
    "permissions",
    "safety_level",
    "risk_tags",
    "compatibility",
    "provenance",
    "license",
    "maintainers",
    "tests",
]


def parse_top_level_yaml(path: Path) -> dict[str, str]:
    """Return top-level YAML keys and their scalar values when present.

    This parser is intentionally small. It supports the simple top-level mapping
    structure used by skill metadata and avoids adding a dependency for the
    initial repository foundation.
    """
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith((" ", "\t", "-")):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def find_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path.parent for path in SKILLS_DIR.rglob("skill.yaml"))


def validate_skill(path: Path) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    for required_file in REQUIRED_FILES:
        if not (path / required_file).exists():
            errors.append(f"missing {required_file}")

    skill_id: str | None = None
    metadata_path = path / "skill.yaml"
    if metadata_path.exists():
        metadata = parse_top_level_yaml(metadata_path)
        skill_id = metadata.get("id") or None
        missing_fields = [field for field in REQUIRED_FIELDS if field not in metadata]
        for field in missing_fields:
            errors.append(f"missing metadata field: {field}")
        if not skill_id:
            errors.append("metadata field id must not be empty")
        if metadata.get("safety_level") not in {"low", "medium", "high", "critical"}:
            errors.append("safety_level must be one of: low, medium, high, critical")

    return skill_id, errors


def main() -> int:
    skill_dirs = find_skill_dirs()
    if not skill_dirs:
        print("FAIL: no skills found under skills/")
        return 1

    print("Awesome Skills Library validation")
    print(f"Found {len(skill_dirs)} skill package(s).")

    failures: list[tuple[Path, list[str]]] = []
    seen_ids: dict[str, Path] = {}

    for skill_dir in skill_dirs:
        skill_id, errors = validate_skill(skill_dir)
        if skill_id:
            if skill_id in seen_ids:
                errors.append(f"duplicate skill id: {skill_id} also used by {seen_ids[skill_id].relative_to(ROOT)}")
            else:
                seen_ids[skill_id] = skill_dir

        rel_path = skill_dir.relative_to(ROOT)
        if errors:
            failures.append((skill_dir, errors))
            print(f"FAIL {rel_path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {rel_path} ({skill_id})")

    if failures:
        print(f"\nValidation failed: {len(failures)} skill package(s) have errors.")
        return 1

    print("\nValidation passed: all skill packages are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
