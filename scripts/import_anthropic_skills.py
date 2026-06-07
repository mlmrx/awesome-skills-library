#!/usr/bin/env python3
"""Index and safely import redistributable Anthropic official skills."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skill_catalog_utils import (
    ATTRIBUTION_PATH,
    JSONL_PATH,
    JSON_PATH,
    SOURCE_AVAILABLE_DOCUMENT_SKILLS,
    THIRD_PARTY_DIR,
    append_jsonl,
    copy_github_folder,
    decode_github_content,
    detect_name_description,
    extract_frontmatter,
    github_api,
    guess_compatibility,
    is_copy_allowed,
    load_json_array,
    redistribution_status,
    risk_tags_for_text,
    slugify,
    stable_id,
    upsert_records,
    utc_now,
    write_json_array,
    write_simple_yaml,
)

OWNER = "anthropics"
REPO = "skills"
REPO_FULL = f"{OWNER}/{REPO}"
REPO_URL = f"https://github.com/{REPO_FULL}"
DOCUMENT_NOTE = "source-available, not open source"


def tree_for_repo(default_branch: str) -> list[dict[str, Any]]:
    data = github_api(f"/repos/{OWNER}/{REPO}/git/trees/{default_branch}", params={"recursive": "1"})
    return data.get("tree", [])


def skill_markdown(ref: str, path: str) -> str:
    item = github_api(f"/repos/{OWNER}/{REPO}/contents/{path}", params={"ref": ref})
    return decode_github_content(item)


def branch_commit(default_branch: str) -> str:
    data = github_api(f"/repos/{OWNER}/{REPO}/branches/{default_branch}")
    return (data.get("commit") or {}).get("sha") or default_branch


def folder_for_skill_path(path: str) -> str:
    parts = Path(path).parts
    return parts[1] if len(parts) > 1 and parts[0] == "skills" else Path(path).parent.name


def license_note(path: str) -> str:
    folder = folder_for_skill_path(path).lower()
    if folder in SOURCE_AVAILABLE_DOCUMENT_SKILLS:
        return DOCUMENT_NOTE
    return "Official Anthropic skill; copied only when repository/per-skill license metadata indicates redistribution is allowed."


def attribution_text(record: dict[str, Any]) -> str:
    return "\n".join([
        "# Attribution",
        "",
        f"- Original skill name: {record['detected_skill_name']}",
        "- Original author or repo owner: Anthropic",
        f"- Source repository: {REPO_FULL}",
        f"- Source URL: {record['file_url']}",
        f"- Original file path: {record['file_path']}",
        f"- Commit SHA: {record['commit_sha']}",
        f"- License name: {record['license_name']}",
        f"- License SPDX ID: {record['license_spdx_id']}",
        f"- Date imported: {record['imported_at']}",
        "- Modifications made, if any: Original files copied without executing imported scripts; attribution metadata added.",
        "",
    ])


def copy_skill(record: dict[str, Any], skill_folder: str, commit_sha: str) -> str:
    destination = THIRD_PARTY_DIR / "anthropics" / slugify(skill_folder)
    copy_github_folder(OWNER, REPO, commit_sha, f"skills/{skill_folder}", destination)
    (destination / "ATTRIBUTION.md").write_text(attribution_text(record), encoding="utf-8")
    write_simple_yaml(destination / "source.yaml", {
        "source_owner": OWNER,
        "source_repo": REPO,
        "source_url": record["file_url"],
        "source_file_path": record["file_path"],
        "source_commit": commit_sha,
        "license_name": record["license_name"],
        "license_spdx_id": record["license_spdx_id"],
        "redistribution_status": "copied",
        "original_author": "Anthropic",
        "imported_at": record["imported_at"],
        "imported_by": "Awesome Skills Library importer",
    })
    return str(destination.relative_to(Path(__file__).resolve().parents[1]))


def main() -> int:
    repo_data = github_api(f"/repos/{OWNER}/{REPO}")
    default_branch = repo_data.get("default_branch") or "main"
    commit_sha = branch_commit(default_branch)
    license_data = repo_data.get("license") or {}
    license_name = license_data.get("name") or "Mixed licensing; see repository and per-skill terms"
    license_spdx = license_data.get("spdx_id") or "NOASSERTION"
    tree = tree_for_repo(default_branch)
    skill_paths = sorted(item["path"] for item in tree if item.get("type") == "blob" and item.get("path", "").startswith("skills/") and item.get("path", "").endswith("/SKILL.md"))
    now = utc_now()
    records: list[dict[str, Any]] = []
    attributions: list[dict[str, Any]] = []

    for path in skill_paths:
        text = skill_markdown(commit_sha, path)
        frontmatter, _ = extract_frontmatter(text)
        skill_folder = folder_for_skill_path(path)
        name, description = detect_name_description(text, skill_folder)
        if frontmatter.get("name"):
            name = str(frontmatter["name"])
        if frontmatter.get("description"):
            description = str(frontmatter["description"])
        file_url = f"{REPO_URL}/blob/{commit_sha}/{path}"
        notes = license_note(path)
        status = redistribution_status(license_spdx, license_name, path, notes)
        copied_to = None
        imported_at = None
        if is_copy_allowed(license_spdx, license_name, path, notes):
            imported_at = now
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
            "raw_url": f"https://raw.githubusercontent.com/{REPO_FULL}/{commit_sha}/{path}",
            "commit_sha": commit_sha,
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
            "imported_at": imported_at,
            "discovery_query": "anthropics/skills skills/*/SKILL.md",
        }
        if imported_at:
            copied_to = copy_skill({**record, "imported_at": imported_at}, skill_folder, commit_sha)
            record["copied_to"] = copied_to
            record["redistribution_status"] = "copied"
        records.append(record)
        attributions.append({
            "skill_id": record["id"],
            "name": name,
            "original_author": "Anthropic",
            "source_repo": REPO_FULL,
            "source_url": file_url,
            "source_file_path": path,
            "source_commit": commit_sha,
            "license_name": record["license_name"],
            "license_spdx_id": record["license_spdx_id"],
            "license_notes": notes,
            "redistribution_status": record["redistribution_status"],
            "copied_to": copied_to,
            "indexed_at": now,
            "imported_at": imported_at,
        })

    write_json_array(JSON_PATH, upsert_records(load_json_array(JSON_PATH), records))
    append_jsonl(JSONL_PATH, records)
    write_json_array(ATTRIBUTION_PATH, upsert_records(load_json_array(ATTRIBUTION_PATH), attributions))
    copied = sum(1 for record in records if record.get("copied_to"))
    document_indexed = sum(1 for record in records if folder_for_skill_path(record["file_path"]) in SOURCE_AVAILABLE_DOCUMENT_SKILLS)
    print(f"indexed {len(records)} Anthropic official skills; copied {copied}; document skills index-only {document_indexed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
