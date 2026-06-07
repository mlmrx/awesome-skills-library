#!/usr/bin/env python3
"""Copy only redistributable discovered third-party skill folders."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from skill_catalog_utils import (
    ATTRIBUTION_PATH,
    JSONL_PATH,
    JSON_PATH,
    THIRD_PARTY_DIR,
    copy_github_folder,
    is_copy_allowed,
    load_json_array,
    read_jsonl,
    redistribution_status,
    slugify,
    stable_id,
    upsert_records,
    utc_now,
    write_json_array,
    write_simple_yaml,
)

ROOT = Path(__file__).resolve().parents[1]


def skill_folder_from_record(record: dict[str, Any]) -> str | None:
    path = record.get("source_file_path") or record.get("file_path")
    if not path:
        return None
    parts = Path(str(path)).parts
    if not parts or parts[-1] != "SKILL.md":
        return None
    return "/".join(parts[:-1])


def owner_repo(record: dict[str, Any]) -> tuple[str, str] | None:
    owner = record.get("source_owner") or record.get("owner")
    repo = record.get("repo")
    source_repo = record.get("source_repo")
    if source_repo and "/" in str(source_repo):
        owner, repo = str(source_repo).split("/", 1)
    if owner and repo:
        return str(owner), str(repo)
    return None


def destination_for(record: dict[str, Any], owner: str, repo: str) -> Path:
    path = str(record.get("source_file_path") or record.get("file_path") or "SKILL.md")
    skill_slug = slugify(record.get("name") or record.get("detected_skill_name") or Path(path).parent.name or repo)
    return THIRD_PARTY_DIR / "community" / f"{slugify(owner)}__{slugify(repo)}__{skill_slug}"


def attribution_text(record: dict[str, Any], owner: str, repo: str, imported_at: str) -> str:
    source_url = record.get("source_file_url") or record.get("file_url") or record.get("source_url") or record.get("repo_url")
    return "\n".join([
        "# Attribution",
        "",
        f"- Original skill name: {record.get('name') or record.get('detected_skill_name') or 'Unknown skill'}",
        f"- Original author or repo owner: {record.get('original_author') or owner}",
        f"- Source repository: {owner}/{repo}",
        f"- Source URL: {source_url}",
        f"- Original file path: {record.get('source_file_path') or record.get('file_path')}",
        f"- Commit SHA: {record.get('source_commit') or record.get('commit_sha') or record.get('default_branch') or record.get('pushed_at')}",
        f"- License name: {record.get('source_license') or record.get('license_name')}",
        f"- License SPDX ID: {record.get('source_license_spdx') or record.get('license_spdx_id')}",
        f"- Date imported: {imported_at}",
        "- Modifications made, if any: Original files copied without executing imported scripts; attribution metadata added.",
        "",
    ])


def source_yaml(record: dict[str, Any], owner: str, repo: str, imported_at: str) -> dict[str, Any]:
    return {
        "source_owner": owner,
        "source_repo": repo,
        "source_url": record.get("source_file_url") or record.get("file_url") or record.get("source_url") or record.get("repo_url"),
        "source_file_path": record.get("source_file_path") or record.get("file_path"),
        "source_commit": record.get("source_commit") or record.get("commit_sha") or record.get("default_branch") or record.get("pushed_at"),
        "license_name": record.get("source_license") or record.get("license_name"),
        "license_spdx_id": record.get("source_license_spdx") or record.get("license_spdx_id"),
        "redistribution_status": "copied",
        "original_author": record.get("original_author") or owner,
        "imported_at": imported_at,
        "imported_by": "Awesome Skills Library importer",
    }


def copy_record(record: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    copied = dict(record)
    pair = owner_repo(record)
    folder = skill_folder_from_record(record)
    if not pair or not folder:
        copied["redistribution_status"] = record.get("redistribution_status") or "index_only"
        copied["trust_notes"] = "No concrete SKILL.md folder path was available to copy."
        return copied
    owner, repo = pair
    license_spdx = copied.get("source_license_spdx") or copied.get("license_spdx_id")
    license_name = copied.get("source_license") or copied.get("license_name")
    status = redistribution_status(license_spdx, license_name, str(copied.get("source_file_path") or copied.get("file_path") or ""), str(copied.get("license_notes") or copied.get("trust_notes") or ""))
    if status == "manual_review":
        copied["redistribution_status"] = "manual_review"
        copied["trust_notes"] = "GPL-family license requires manual review before redistribution in this library."
        return copied
    if not is_copy_allowed(license_spdx, license_name, str(copied.get("source_file_path") or copied.get("file_path") or ""), str(copied.get("license_notes") or copied.get("trust_notes") or "")):
        copied["redistribution_status"] = "index_only" if status in {"index_only", "unknown"} else status
        copied["trust_notes"] = copied.get("trust_notes") or "License is missing, unknown, proprietary, source-available, or unclear; cataloged only."
        return copied
    ref = str(copied.get("source_commit") or copied.get("commit_sha") or copied.get("default_branch") or "HEAD")
    imported_at = utc_now()
    destination = destination_for(copied, owner, repo)
    if not dry_run:
        copy_github_folder(owner, repo, ref, folder, destination)
        (destination / "ATTRIBUTION.md").write_text(attribution_text(copied, owner, repo, imported_at), encoding="utf-8")
        write_simple_yaml(destination / "source.yaml", source_yaml(copied, owner, repo, imported_at))
    copied["redistribution_status"] = "copied"
    copied["copied_to"] = str(destination.relative_to(ROOT))
    copied["imported_at"] = imported_at
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy discovered third-party skills when their licenses allow redistribution.")
    parser.add_argument("--dry-run", action="store_true", help="Classify records but do not download or copy files.")
    args = parser.parse_args()

    raw_records = upsert_records([], load_json_array(JSON_PATH) + read_jsonl(JSONL_PATH))
    processed: list[dict[str, Any]] = []
    attributions: list[dict[str, Any]] = []
    for record in raw_records:
        if record.get("source_repo") == "anthropics/skills" or record.get("source_type") == "official":
            processed.append(record)
            continue
        updated = copy_record(record, dry_run=args.dry_run)
        processed.append(updated)
        if updated.get("redistribution_status") == "copied":
            attributions.append({
                "skill_id": updated.get("id") or stable_id(str(updated.get("source_repo") or ""), str(updated.get("source_file_path") or updated.get("file_path") or "")),
                "name": updated.get("name") or updated.get("detected_skill_name"),
                "original_author": updated.get("original_author") or updated.get("owner"),
                "source_repo": updated.get("source_repo"),
                "source_url": updated.get("source_file_url") or updated.get("file_url") or updated.get("source_url"),
                "source_file_path": updated.get("source_file_path") or updated.get("file_path"),
                "source_commit": updated.get("source_commit") or updated.get("commit_sha"),
                "license_name": updated.get("source_license") or updated.get("license_name"),
                "license_spdx_id": updated.get("source_license_spdx") or updated.get("license_spdx_id"),
                "redistribution_status": "copied",
                "copied_to": updated.get("copied_to"),
                "imported_at": updated.get("imported_at"),
            })
    write_json_array(JSON_PATH, upsert_records([], processed))
    JSONL_PATH.write_text("", encoding="utf-8")
    from skill_catalog_utils import append_jsonl
    append_jsonl(JSONL_PATH, upsert_records([], processed))
    write_json_array(ATTRIBUTION_PATH, upsert_records(load_json_array(ATTRIBUTION_PATH), attributions))
    print(f"processed {len(processed)} records; copied {sum(1 for r in processed if r.get('redistribution_status') == 'copied')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
