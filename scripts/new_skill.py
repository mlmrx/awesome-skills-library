#!/usr/bin/env python3
"""Create a new skill package from templates/skill."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "skill"
SKILLS_DIR = ROOT / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new skill package from the template.")
    parser.add_argument("path", help="Skill path in the form <category>/<skill-slug>")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing skill directory")
    return parser.parse_args()


def validate_skill_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("path must be relative and must not contain '..'")
    if len(path.parts) != 2:
        raise ValueError("path must be in the form <category>/<skill-slug>")
    return path


def update_placeholders(skill_dir: Path, category: str, slug: str) -> None:
    skill_name = slug.replace("-", " ").title()
    skill_id = f"{category}.{slug}"
    yaml_path = skill_dir / "skill.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    text = text.replace("category.skill-slug", skill_id)
    text = text.replace("Skill Name", skill_name)
    text = text.replace("category: category", f"category: {category}", 1)
    yaml_path.write_text(text, encoding="utf-8")

    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8").replace("# Skill Name", f"# {skill_name}", 1)
    skill_md.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        rel_path = validate_skill_path(args.path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    target_dir = SKILLS_DIR / rel_path
    if target_dir.exists():
        if not args.force:
            print(f"ERROR: {target_dir.relative_to(ROOT)} already exists. Use --force to overwrite.", file=sys.stderr)
            return 1
        shutil.rmtree(target_dir)

    shutil.copytree(TEMPLATE_DIR, target_dir)
    update_placeholders(target_dir, rel_path.parts[0], rel_path.parts[1])

    print(f"Created {target_dir.relative_to(ROOT)}")
    print("Next steps:")
    print("  1. Edit SKILL.md with a concrete workflow and safety boundaries.")
    print("  2. Complete skill.yaml metadata.")
    print("  3. Update tests/basic.yaml and examples/.")
    print("  4. Run: python scripts/validate_skills.py")
    print("  5. Run: python scripts/generate_index.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
