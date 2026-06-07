#!/usr/bin/env python3
"""Validate attribution metadata for copied third-party skills."""

from __future__ import annotations

import sys
from pathlib import Path

from skill_catalog_utils import ROOT, SOURCE_AVAILABLE_DOCUMENT_SKILLS, read_simple_yaml

THIRD_PARTY = ROOT / "third_party" / "skills"
ANTHROPIC = THIRD_PARTY / "anthropics"


def copied_skill_dirs() -> list[Path]:
    if not THIRD_PARTY.exists():
        return []
    return sorted(path.parent for path in THIRD_PARTY.rglob("source.yaml") if path.parent.is_dir())


def main() -> int:
    errors: list[str] = []
    for skill_dir in copied_skill_dirs():
        attribution = skill_dir / "ATTRIBUTION.md"
        source = skill_dir / "source.yaml"
        rel = skill_dir.relative_to(ROOT)
        if not attribution.exists():
            errors.append(f"{rel} is missing ATTRIBUTION.md")
        if not source.exists():
            errors.append(f"{rel} is missing source.yaml")
            continue
        data = read_simple_yaml(source)
        license_spdx = data.get("license_spdx_id", "").strip()
        if not data.get("license_name") or not license_spdx:
            errors.append(f"{rel}/source.yaml is missing license info")
        if not data.get("source_url"):
            errors.append(f"{rel}/source.yaml is missing source_url")
        if not (data.get("source_commit") or data.get("source_timestamp")):
            errors.append(f"{rel}/source.yaml is missing source_commit or source_timestamp")
        if license_spdx == "NOASSERTION":
            errors.append(f"{rel}/source.yaml has license_spdx_id: NOASSERTION")
        if data.get("redistribution_status") == "unknown":
            errors.append(f"{rel}/source.yaml has redistribution_status: unknown")
    for name in SOURCE_AVAILABLE_DOCUMENT_SKILLS:
        if (ANTHROPIC / name).exists():
            errors.append(f"Anthropic document skill must not be copied: {ANTHROPIC / name}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"validated attribution metadata for {len(copied_skill_dirs())} copied third-party skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
