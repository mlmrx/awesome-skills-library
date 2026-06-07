#!/usr/bin/env python3
"""Generate a Markdown report for the skill acquisition catalog."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from skill_catalog_utils import JSON_PATH, ROOT, SOURCES_PATH, load_json_array, utc_now

REPORT_PATH = ROOT / "catalog" / "import-report.md"


def count_enabled_sources() -> int:
    if not SOURCES_PATH.exists():
        return 0
    count = 0
    in_source = False
    for line in SOURCES_PATH.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:"):
            in_source = True
        elif in_source and stripped == "enabled: true":
            count += 1
            in_source = False
    return count


def table(counter: Counter[str], headers: tuple[str, str]) -> str:
    if not counter:
        return "_None._\n"
    lines = [f"| {headers[0]} | {headers[1]} |", "| --- | ---: |"]
    for key, value in counter.most_common():
        lines.append(f"| {key or 'unknown'} | {value} |")
    return "\n".join(lines) + "\n"


def duplicate_names(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record.get("name") or "").strip().lower()].append(record)
    return {name: items for name, items in grouped.items() if name and len(items) > 1}


def main() -> int:
    records = load_json_array(JSON_PATH)
    source_count = count_enabled_sources()
    official = [r for r in records if r.get("source_repo") == "anthropics/skills" or r.get("source_type") == "official"]
    repo_counts = Counter(str(r.get("source_repo") or "unknown") for r in records)
    license_counts = Counter(str(r.get("source_license_spdx") or r.get("source_license") or "unknown") for r in records)
    redistribution_counts = Counter(str(r.get("redistribution_status") or "unknown") for r in records)
    category_counts = Counter(str(r.get("category_guess") or "unknown") for r in records)
    manual_review = [r for r in records if r.get("redistribution_status") in {"unknown", "index_only", "prohibited"} or r.get("risk_tags")]
    duplicates = duplicate_names(records)
    high_risk_tags = {"credentials", "api_keys", "payments", "destructive_actions", "security_bypass", "code_execution", "database_access"}
    high_risk = [r for r in records if high_risk_tags.intersection(set(r.get("risk_tags") or []))]

    lines = [
        "# Skill acquisition import report",
        "",
        f"Generated at: `{utc_now()}`",
        "",
        "## Summary",
        "",
        f"- Total sources scanned/configured: **{source_count}**",
        f"- Total candidate skills found: **{len(records)}**",
        f"- Total Anthropic official skills found: **{len(official)}**",
        "",
        "## Top repositories by number of skills",
        "",
        table(repo_counts, ("Repository", "Skills")),
        "## License breakdown",
        "",
        table(license_counts, ("License", "Skills")),
        "## Redistribution status breakdown",
        "",
        table(redistribution_counts, ("Status", "Skills")),
        "## Category breakdown",
        "",
        table(category_counts, ("Category", "Skills")),
        "## Skills requiring manual review",
        "",
    ]
    if manual_review:
        lines.extend(["| Skill | Source | Reason |", "| --- | --- | --- |"])
        for record in manual_review[:100]:
            reasons = []
            if record.get("redistribution_status") in {"unknown", "index_only", "prohibited"}:
                reasons.append(f"redistribution={record.get('redistribution_status')}")
            if record.get("risk_tags"):
                reasons.append("risk_tags=" + ", ".join(record.get("risk_tags") or []))
            lines.append(f"| {record.get('name') or 'unknown'} | {record.get('source_file_url') or record.get('source_url') or record.get('source_repo')} | {'; '.join(reasons)} |")
    else:
        lines.append("_None._")
    lines.extend(["", "## Duplicate or near-duplicate skill names", ""])
    if duplicates:
        lines.extend(["| Name | Sources |", "| --- | --- |"])
        for name, items in sorted(duplicates.items()):
            sources = "; ".join(str(item.get("source_file_url") or item.get("source_repo")) for item in items)
            lines.append(f"| {name} | {sources} |")
    else:
        lines.append("_None detected._")
    lines.extend(["", "## High-risk candidates", ""])
    if high_risk:
        lines.extend(["| Skill | Source | Risk tags |", "| --- | --- | --- |"])
        for record in high_risk[:100]:
            lines.append(f"| {record.get('name') or 'unknown'} | {record.get('source_file_url') or record.get('source_url') or record.get('source_repo')} | {', '.join(record.get('risk_tags') or [])} |")
    else:
        lines.append("_None detected._")
    lines.extend([
        "",
        "## Next recommended sources to scan",
        "",
        "- GitHub repositories tagged `claude-skills`, `agent-skills`, `claude-code-skills`, and `codex-skills`.",
        "- Awesome lists that link to individual skill repositories, with per-link license review.",
        "- Official runtime-specific skill registries or marketplaces once their redistribution policies are documented.",
        "- Research repositories that publish agent workflows with explicit open-source licenses.",
        "",
        "## Notes",
        "",
        "This report is generated from metadata only. Unknown-license and source-available candidates remain index-only until manual review confirms redistribution permissions.",
    ])
    REPORT_PATH.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
