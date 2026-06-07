#!/usr/bin/env python3
"""Generate a Markdown report for the licensed skill import catalog."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from skill_catalog_utils import JSON_PATH, ROOT, SOURCE_AVAILABLE_DOCUMENT_SKILLS, SOURCES_PATH, load_json_array, utc_now

REPORT_PATH = ROOT / "catalog" / "import-report.md"


def count_enabled_sources() -> int:
    if not SOURCES_PATH.exists():
        return 0
    return sum(1 for line in SOURCES_PATH.read_text(encoding="utf-8").splitlines() if line.strip() == "enabled: true")


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
    official = [r for r in records if r.get("source_repo") == "anthropics/skills" or r.get("source_type") == "official"]
    copied = [r for r in records if r.get("redistribution_status") == "copied" or r.get("copied_to")]
    index_only = [r for r in records if r.get("redistribution_status") == "index_only"]
    manual_review = [r for r in records if r.get("redistribution_status") == "manual_review"]
    unknown = [r for r in records if r.get("redistribution_status") == "unknown" or not r.get("source_license_spdx") or r.get("source_license_spdx") == "NOASSERTION"]
    anthropic_copied = [r for r in official if r.get("copied_to")]
    anthropic_doc_indexed = [
        r for r in official
        if (r.get("source_file_path") or "").split("/")[1:2]
        and (r.get("source_file_path") or "").split("/")[1] in SOURCE_AVAILABLE_DOCUMENT_SKILLS
        and not r.get("copied_to")
    ]
    risk_counter: Counter[str] = Counter()
    for record in records:
        risk_counter.update(record.get("risk_tags") or [])
    duplicates = duplicate_names(records)

    lines = [
        "# Skill acquisition import report",
        "",
        f"Generated at: `{utc_now()}`",
        "",
        "## Summary",
        "",
        f"- Sources scanned/configured: **{count_enabled_sources()}**",
        f"- Total candidate skills found: **{len(records)}**",
        f"- Total skills copied: **{len(copied)}**",
        f"- Total index-only skills: **{len(index_only)}**",
        f"- Total manual-review skills: **{len(manual_review)}**",
        f"- Total unknown-license skills: **{len(unknown)}**",
        f"- Anthropic official skills copied: **{len(anthropic_copied)}**",
        f"- Anthropic source-available document skills indexed only: **{len(anthropic_doc_indexed)}**",
        "",
        "## Top repositories by number of skills",
        "",
        table(Counter(str(r.get("source_repo") or "unknown") for r in records), ("Repository", "Skills")),
        "## License breakdown",
        "",
        table(Counter(str(r.get("source_license_spdx") or r.get("source_license") or "unknown") for r in records), ("License", "Skills")),
        "## Redistribution status breakdown",
        "",
        table(Counter(str(r.get("redistribution_status") or "unknown") for r in records), ("Status", "Skills")),
        "## Category breakdown",
        "",
        table(Counter(str(r.get("category_guess") or "unknown") for r in records), ("Category", "Skills")),
        "## Risk tag breakdown",
        "",
        table(risk_counter, ("Risk tag", "Skills")),
        "## Duplicate skill names",
        "",
    ]
    if duplicates:
        lines.extend(["| Name | Sources |", "| --- | --- |"])
        for name, items in sorted(duplicates.items()):
            sources = "; ".join(str(item.get("source_file_url") or item.get("source_repo")) for item in items)
            lines.append(f"| {name} | {sources} |")
    else:
        lines.append("_None detected._")

    lines.extend(["", "## Copied destination paths", ""])
    if copied:
        lines.extend(["| Skill | Destination | Source |", "| --- | --- | --- |"])
        for record in copied:
            lines.append(f"| {record.get('name') or 'unknown'} | {record.get('copied_to')} | {record.get('source_file_url') or record.get('source_url')} |")
    else:
        lines.append("_No skills copied yet._")

    lines.extend(["", "## Manual review queue", ""])
    queue = manual_review + [r for r in unknown if r not in manual_review] + [r for r in index_only if r not in unknown and r.get("source_repo") != "anthropics/skills"]
    if queue:
        lines.extend(["| Skill | Source | Reason |", "| --- | --- | --- |"])
        for record in queue[:200]:
            reason = record.get("trust_notes") or record.get("license_notes") or f"redistribution={record.get('redistribution_status')}"
            lines.append(f"| {record.get('name') or 'unknown'} | {record.get('source_file_url') or record.get('source_url') or record.get('source_repo')} | {reason} |")
    else:
        lines.append("_None._")

    lines.extend([
        "",
        "## Notes",
        "",
        "Discovery and import scripts never execute imported skill scripts or install imported dependencies. Unknown-license, proprietary, unclear, and source-available candidates remain catalog-only until manual review confirms redistribution permission.",
    ])
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
