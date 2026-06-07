#!/usr/bin/env python3
"""Discover public GitHub repositories/files that look like AI agent skills.

The script indexes metadata and, when needed, fetches only candidate SKILL.md
files. It never clones or downloads whole repositories.
"""

from __future__ import annotations

import argparse
from typing import Any

from skill_catalog_utils import (
    JSONL_PATH,
    detect_name_description,
    github_api,
    risk_tags_for_text,
    utc_now,
    append_jsonl,
)

DEFAULT_QUERIES = [
    'filename:SKILL.md "description"',
    'filename:SKILL.md "Claude"',
    'filename:SKILL.md "agent skill"',
    'topic:claude-skills',
    'topic:agent-skills',
    'topic:claude-code-skills',
    'topic:codex-skills',
    '"SKILL.md" "Claude Code"',
    '"SKILL.md" "Agent Skills"',
]


def repo_metadata(owner: str, repo: str, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    key = f"{owner}/{repo}"
    if key not in cache:
        cache[key] = github_api(f"/repos/{owner}/{repo}")
    return cache[key]


def content_text(owner: str, repo: str, path: str, ref: str | None) -> str:
    params = {"ref": ref} if ref else None
    item = github_api(f"/repos/{owner}/{repo}/contents/{path}", params=params)
    from skill_catalog_utils import decode_github_content

    return decode_github_content(item)


def search_code(query: str, max_remaining: int, per_page: int, repo_cache: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    page = 1
    while max_remaining > 0:
        data = github_api("/search/code", params={"q": query, "per_page": min(per_page, max_remaining, 100), "page": page})
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            if max_remaining <= 0:
                break
            repo_info = item.get("repository") or {}
            full_name = repo_info.get("full_name", "")
            if "/" not in full_name:
                continue
            owner, repo = full_name.split("/", 1)
            repo_data = repo_metadata(owner, repo, repo_cache)
            default_branch = repo_data.get("default_branch") or "main"
            path = item.get("path") or "SKILL.md"
            text = ""
            try:
                text = content_text(owner, repo, path, default_branch)
            except Exception as exc:  # candidate metadata is still useful
                text = f"Fetch failed for risk/name detection: {exc}"
            fallback_name = path.split("/")[-2] if "/" in path else repo
            name, description = detect_name_description(text, fallback_name)
            license_data = repo_data.get("license") or {}
            html_url = item.get("html_url") or f"https://github.com/{full_name}/blob/{default_branch}/{path}"
            raw_url = f"https://raw.githubusercontent.com/{full_name}/{default_branch}/{path}"
            records.append({
                "source_repo": full_name,
                "owner": owner,
                "repo": repo,
                "repo_url": repo_data.get("html_url") or f"https://github.com/{full_name}",
                "default_branch": default_branch,
                "file_path": path,
                "file_url": html_url,
                "raw_url": raw_url,
                "detected_skill_name": name,
                "detected_description": description,
                "topics": repo_data.get("topics") or [],
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "repo_description": repo_data.get("description") or "",
                "license_name": license_data.get("name") if license_data else None,
                "license_spdx_id": license_data.get("spdx_id") if license_data else None,
                "last_updated_at": repo_data.get("updated_at"),
                "pushed_at": repo_data.get("pushed_at"),
                "discovered_at": utc_now(),
                "discovery_query": query,
                "risk_tags": risk_tags_for_text(text),
                "record_type": "github_discovery",
            })
            max_remaining -= 1
        if len(items) < per_page or max_remaining <= 0:
            break
        page += 1
    return records


def search_repositories(query: str, max_remaining: int, per_page: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    page = 1
    while max_remaining > 0:
        data = github_api("/search/repositories", params={"q": query, "per_page": min(per_page, max_remaining, 100), "page": page})
        items = data.get("items", [])
        if not items:
            break
        for repo_data in items:
            if max_remaining <= 0:
                break
            full_name = repo_data.get("full_name", "")
            if "/" not in full_name:
                continue
            owner, repo = full_name.split("/", 1)
            default_branch = repo_data.get("default_branch") or "main"
            license_data = repo_data.get("license") or {}
            records.append({
                "source_repo": full_name,
                "owner": owner,
                "repo": repo,
                "repo_url": repo_data.get("html_url") or f"https://github.com/{full_name}",
                "default_branch": default_branch,
                "file_path": None,
                "file_url": repo_data.get("html_url"),
                "raw_url": None,
                "detected_skill_name": repo_data.get("name") or repo,
                "detected_description": repo_data.get("description") or "",
                "topics": repo_data.get("topics") or [],
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "repo_description": repo_data.get("description") or "",
                "license_name": license_data.get("name") if license_data else None,
                "license_spdx_id": license_data.get("spdx_id") if license_data else None,
                "last_updated_at": repo_data.get("updated_at"),
                "pushed_at": repo_data.get("pushed_at"),
                "discovered_at": utc_now(),
                "discovery_query": query,
                "risk_tags": [],
                "record_type": "github_repository_topic",
            })
            max_remaining -= 1
        if len(items) < per_page or max_remaining <= 0:
            break
        page += 1
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover GitHub skill candidates without cloning repositories.")
    parser.add_argument("--max-results", type=int, default=250, help="Maximum records to append across all queries.")
    parser.add_argument("--per-page", type=int, default=50, help="GitHub search page size, max 100.")
    parser.add_argument("--output", default=str(JSONL_PATH), help="JSONL output path.")
    parser.add_argument("--query", action="append", help="Additional or replacement query. Repeatable.")
    args = parser.parse_args()

    queries = args.query or DEFAULT_QUERIES
    remaining = args.max_results
    repo_cache: dict[str, dict[str, Any]] = {}
    all_records: list[dict[str, Any]] = []
    for query in queries:
        if remaining <= 0:
            break
        try:
            if query.startswith("topic:"):
                records = search_repositories(query, remaining, args.per_page)
            else:
                records = search_code(query, remaining, args.per_page, repo_cache)
        except Exception as exc:
            print(f"warning: query failed {query!r}: {exc}")
            continue
        all_records.extend(records)
        remaining -= len(records)
        print(f"{query}: {len(records)} records")
    append_jsonl(__import__("pathlib").Path(args.output), all_records)
    print(f"appended {len(all_records)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
