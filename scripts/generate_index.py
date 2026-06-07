#!/usr/bin/env python3
"""Generate SKILLS_INDEX.md from skill.yaml files."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
INDEX_PATH = ROOT / "SKILLS_INDEX.md"


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_skills import COMPATIBILITY_FIELDS, load_yaml  # noqa: E402


def scalar_string(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def compatibility_summary(metadata: dict[str, Any]) -> str:
    compatibility = metadata.get("compatibility")
    if not isinstance(compatibility, dict):
        return "unknown"
    supported = [
        f"{target}: {compatibility[target]}"
        for target in COMPATIBILITY_FIELDS
        if isinstance(compatibility.get(target), str) and compatibility[target] != "unknown"
    ]
    return ", ".join(supported) if supported else "unknown"


def collect_skills() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for metadata_path in sorted(SKILLS_DIR.rglob("skill.yaml")):
        metadata = load_yaml(metadata_path)
        skill_dir = metadata_path.parent
        category = scalar_string(metadata.get("category"), "uncategorized")
        grouped[category].append(
            {
                "name": scalar_string(metadata.get("name"), "Unnamed skill"),
                "id": scalar_string(metadata.get("id"), "unknown"),
                "description": scalar_string(metadata.get("description")),
                "safety_level": scalar_string(metadata.get("safety_level"), "unknown"),
                "compatibility": compatibility_summary(metadata),
                "link": skill_dir.relative_to(ROOT).as_posix(),
            }
        )
    return grouped


def render_index(grouped: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        "# Skills Index",
        "",
        "This index is generated from `skill.yaml` files by `python scripts/generate_index.py`.",
        "",
    ]
    if not grouped:
        lines.extend(["No skills are currently registered.", ""])
        return "\n".join(lines)

    for category in sorted(grouped):
        lines.extend([f"## {category}", ""])
        lines.append("| Skill | ID | Description | Safety level | Compatibility | Folder |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for skill in sorted(grouped[category], key=lambda item: item["name"].lower()):
            lines.append(
                "| {name} | `{id}` | {description} | {safety_level} | {compatibility} | [{link}]({link}) |".format(
                    **skill
                )
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    grouped = collect_skills()
    INDEX_PATH.write_text(render_index(grouped), encoding="utf-8")
    total = sum(len(skills) for skills in grouped.values())
    print(f"Generated {INDEX_PATH.relative_to(ROOT)} with {total} skill(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
