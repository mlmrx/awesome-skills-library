#!/usr/bin/env python3
"""Normalize discovered skill metadata into the common catalog schema."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from skill_catalog_utils import (
    ATTRIBUTION_PATH,
    JSONL_PATH,
    JSON_PATH,
    append_jsonl,
    guess_category,
    guess_compatibility,
    load_json_array,
    read_jsonl,
    redistribution_status,
    stable_id,
    upsert_records,
    utc_now,
    write_json_array,
)


def source_type(record: dict[str, Any]) -> str:
    if record.get("source_type"):
        return str(record["source_type"])
    if record.get("source_repo") == "anthropics/skills":
        return "official"
    query = str(record.get("discovery_query") or "").lower()
    repo = str(record.get("source_repo") or "").lower()
    if "awesome" in query or "awesome" in repo:
        return "awesome-list"
    if "marketplace" in query or "marketplace" in repo:
        return "marketplace"
    if "research" in query:
        return "research"
    return "community"


def bool_from_path(record: dict[str, Any], needles: list[str]) -> bool:
    text = " ".join(str(record.get(key) or "") for key in ("file_path", "repo_description", "detected_description")).lower()
    return any(needle in text for needle in needles)


def normalize(record: dict[str, Any], now: str) -> dict[str, Any]:
    source_repo = str(record.get("source_repo") or f"{record.get('owner', '')}/{record.get('repo', '')}").strip("/")
    owner = str(record.get("owner") or source_repo.split("/")[0] if source_repo else record.get("repo_owner") or "")
    repo = str(record.get("repo") or source_repo.split("/")[-1] if source_repo else record.get("repo_name") or "")
    path = str(record.get("file_path") or record.get("source_file_path") or "")
    name = str(record.get("detected_skill_name") or record.get("name") or Path(path).parent.name or repo or "Unknown skill")
    description = str(record.get("detected_description") or record.get("description") or record.get("repo_description") or "")
    license_name = record.get("license_name") or record.get("source_license")
    license_spdx = record.get("license_spdx_id") or record.get("source_license_spdx")
    status = record.get("redistribution_status") or redistribution_status(license_spdx, license_name, path, str(record.get("license_notes") or ""))
    topics = record.get("topics") or record.get("repo_topics") or []
    compatibility = record.get("compatibility_guess") or guess_compatibility(name, description, path, topics, source_repo)
    if isinstance(compatibility, str):
        compatibility = [compatibility]
    return {
        "id": record.get("id") or stable_id(source_repo, path, name),
        "name": name,
        "description": description,
        "source_type": source_type(record),
        "source_owner": owner,
        "source_repo": source_repo,
        "source_url": record.get("repo_url") or (f"https://github.com/{source_repo}" if source_repo else None),
        "source_file_path": path or None,
        "source_file_url": (
            record.get("file_url")
            or record.get("source_file_url")
            or record.get("raw_url")
            or (f"https://github.com/{source_repo}/blob/main/{path}" if source_repo and path else None)
        ),
        "source_license": license_name,
        "source_license_spdx": license_spdx,
        "source_commit": record.get("source_commit") or record.get("commit_sha"),
        "redistribution_status": status,
        "copied_to": record.get("copied_to"),
        "original_author": record.get("original_author") or ("Anthropic" if source_repo == "anthropics/skills" else owner),
        "repo_owner": owner,
        "repo_stars": record.get("stars") or record.get("repo_stars") or 0,
        "repo_topics": topics,
        "category_guess": record.get("category_guess") or guess_category(name, description, path, topics),
        "compatibility_guess": compatibility,
        "has_scripts": bool(record.get("has_scripts")) or bool_from_path(record, ["script", "scripts/", ".py", ".sh", "automation"]),
        "has_resources": bool(record.get("has_resources")) or bool_from_path(record, ["resource", "resources/", "assets/", "template"]),
        "has_tests": bool(record.get("has_tests")) or bool_from_path(record, ["test", "tests/", "spec"]),
        "risk_tags": sorted(set(record.get("risk_tags") or [])),
        "trust_notes": record.get("trust_notes") or record.get("license_notes") or "Requires manual review before any content import.",
        "discovered_at": record.get("discovered_at") or now,
        "imported_at": record.get("imported_at"),
        "last_seen_at": now,
    }


def main() -> int:
    now = utc_now()
    raw_records = load_json_array(JSON_PATH) + read_jsonl(JSONL_PATH)
    normalized = [normalize(record, now) for record in raw_records]
    normalized = upsert_records([], normalized)
    write_json_array(JSON_PATH, normalized)
    # Rewrite JSONL with normalized records to keep the stream searchable and deduplicated.
    JSONL_PATH.write_text("")
    append_jsonl(JSONL_PATH, normalized)

    attributions = []
    for record in normalized:
        attributions.append({
            "skill_id": record["id"],
            "name": record["name"],
            "original_author": record["original_author"],
            "source_repo": record["source_repo"],
            "source_url": record["source_file_url"] or record["source_url"],
            "source_file_path": record.get("source_file_path"),
            "source_commit": record.get("source_commit"),
            "copied_to": record.get("copied_to"),
            "imported_at": record.get("imported_at"),
            "license_name": record["source_license"],
            "license_spdx_id": record["source_license_spdx"],
            "redistribution_status": record["redistribution_status"],
            "attribution_required": record["redistribution_status"] in {"allowed", "attribution_required"},
            "last_seen_at": record["last_seen_at"],
        })
    write_json_array(ATTRIBUTION_PATH, upsert_records([], attributions))
    print(f"normalized {len(normalized)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
