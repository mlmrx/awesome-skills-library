#!/usr/bin/env python3
"""Index Anthropic official skills metadata with attribution and license notes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skill_catalog_utils import (
    ATTRIBUTION_PATH,
    JSONL_PATH,
    JSON_PATH,
    SOURCE_AVAILABLE_DOCUMENT_SKILLS,
    append_jsonl,
    decode_github_content,
    detect_name_description,
    extract_frontmatter,
    github_api,
    guess_compatibility,
    load_json_array,
    redistribution_status,
    risk_tags_for_text,
    stable_id,
    upsert_records,
    utc_now,
    write_json_array,
)

OWNER = "anthropics"
REPO = "skills"
REPO_FULL = f"{OWNER}/{REPO}"
REPO_URL = f"https://github.com/{REPO_FULL}"


def tree_for_repo(default_branch: str) -> list[dict[str, Any]]:
    data = github_api(f"/repos/{OWNER}/{REPO}/git/trees/{default_branch}", params={"recursive": "1"})
    return data.get("tree", [])


def skill_markdown(default_branch: str, path: str) -> str:
    item = github_api(f"/repos/{OWNER}/{REPO}/contents/{path}", params={"ref": default_branch})
    return decode_github_content(item)


def license_note(path: str) -> str:
    parts = Path(path).parts
    folder = parts[1] if len(parts) > 1 and parts[0] == "skills" else Path(path).parent.name
    if folder.lower() in SOURCE_AVAILABLE_DOCUMENT_SKILLS:
        return "Anthropic document skill is source-available reference material; index metadata only and do not copy content without explicit permission."
    return "Official Anthropic skill metadata indexed with attribution; verify repository and per-folder license before redistribution."


def main() -> int:
    repo_data = github_api(f"/repos/{OWNER}/{REPO}")
    default_branch = repo_data.get("default_branch") or "main"
    license_data = repo_data.get("license") or {}
    license_name = license_data.get("name") or "Mixed licensing; see repository and per-skill terms"
    license_spdx = license_data.get("spdx_id") or "NOASSERTION"
    tree = tree_for_repo(default_branch)
    skill_paths = sorted(item["path"] for item in tree if item.get("type") == "blob" and item.get("path", "").startswith("skills/") and item.get("path", "").endswith("/SKILL.md"))
    now = utc_now()
    records: list[dict[str, Any]] = []
    attributions: list[dict[str, Any]] = []

    for path in skill_paths:
        text = skill_markdown(default_branch, path)
        frontmatter, _ = extract_frontmatter(text)
        fallback_name = Path(path).parent.name
        name, description = detect_name_description(text, fallback_name)
        if frontmatter.get("name"):
            name = str(frontmatter["name"])
        if frontmatter.get("description"):
            description = str(frontmatter["description"])
        file_url = f"{REPO_URL}/blob/{default_branch}/{path}"
        raw_url = f"https://raw.githubusercontent.com/{REPO_FULL}/{default_branch}/{path}"
        notes = license_note(path)
        status = redistribution_status(license_spdx, license_name, path, notes)
        record = {
            "id": stable_id(REPO_FULL, path),
            "record_type": "anthropic_official",
            "source_type": "official",
            "source_repo": REPO_FULL,
            "owner": OWNER,
            "repo": REPO,
            "repo_url": REPO_URL,
            "default_branch": default_branch,
            "file_path": path,
            "file_url": file_url,
            "raw_url": raw_url,
            "detected_skill_name": name,
            "detected_description": description,
            "frontmatter": frontmatter,
            "topics": repo_data.get("topics") or [],
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "repo_description": repo_data.get("description") or "",
            "license_name": license_name,
            "license_spdx_id": license_spdx,
            "license_notes": notes,
            "redistribution_status": status,
            "compatibility_guess": guess_compatibility(path, text, repo_data.get("topics") or []),
            "risk_tags": risk_tags_for_text(text),
            "last_updated_at": repo_data.get("updated_at"),
            "pushed_at": repo_data.get("pushed_at"),
            "discovered_at": now,
            "discovery_query": "anthropics/skills skills/*/SKILL.md",
        }
        records.append(record)
        attributions.append({
            "skill_id": record["id"],
            "name": name,
            "original_author": "Anthropic",
            "source_repo": REPO_FULL,
            "source_url": file_url,
            "license_name": record["license_name"],
            "license_spdx_id": record["license_spdx_id"],
            "license_notes": notes,
            "redistribution_status": status,
            "indexed_at": now,
        })

    existing = load_json_array(JSON_PATH)
    write_json_array(JSON_PATH, upsert_records(existing, records))
    append_jsonl(JSONL_PATH, records)
    existing_attr = load_json_array(ATTRIBUTION_PATH)
    write_json_array(ATTRIBUTION_PATH, upsert_records(existing_attr, attributions))
    print(f"indexed {len(records)} Anthropic official skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
