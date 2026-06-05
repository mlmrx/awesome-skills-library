#!/usr/bin/env python3
"""Generate SKILLS_INDEX.md from skill.yaml files."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
INDEX_PATH = ROOT / "SKILLS_INDEX.md"


def parse_top_level_yaml(path: Path) -> dict[str, str]:
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


def simple_list_value(path: Path, key: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    key_indent: int | None = None
    values: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        if key_indent is None:
            if stripped.startswith(f"{key}:"):
                key_indent = indent
            continue
        if indent <= key_indent and not stripped.startswith("-"):
            break
        if stripped.startswith("-"):
            values.append(stripped[1:].strip())
    return ", ".join(values) if values else "unknown"


def compatibility_summary(path: Path) -> str:
    runtimes = simple_list_value(path, "agent_runtimes")
    return runtimes if runtimes != "unknown" else "see skill.yaml"


def collect_skills() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for metadata_path in sorted(SKILLS_DIR.rglob("skill.yaml")):
        metadata = parse_top_level_yaml(metadata_path)
        skill_dir = metadata_path.parent
        category = metadata.get("category", "uncategorized")
        grouped[category].append(
            {
                "name": metadata.get("name", "Unnamed skill"),
                "id": metadata.get("id", "unknown"),
                "description": metadata.get("description", ""),
                "safety_level": metadata.get("safety_level", "unknown"),
                "compatibility": compatibility_summary(metadata_path),
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
