#!/usr/bin/env python3
"""Shared helpers for attribution-first skill catalog scripts."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
JSON_PATH = CATALOG_DIR / "discovered-skills.json"
JSONL_PATH = CATALOG_DIR / "discovered-skills.jsonl"
ATTRIBUTION_PATH = CATALOG_DIR / "attribution.json"
SOURCES_PATH = CATALOG_DIR / "sources.yaml"
THIRD_PARTY_DIR = ROOT / "third_party" / "skills"
CACHE_DIR = ROOT / ".cache" / "skills"

ALLOWED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"}
GPL_FAMILY_LICENSES = {"GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "AGPL-3.0"}
PUBLIC_DOMAIN_LICENSES = {"CC0-1.0", "Unlicense"}
REDISTRIBUTABLE_LICENSES = ALLOWED_LICENSES | PUBLIC_DOMAIN_LICENSES
SOURCE_AVAILABLE_DOCUMENT_SKILLS = {"docx", "pdf", "pptx", "xlsx"}

RISK_KEYWORDS = {
    "shell_commands": ["shell", "bash", "terminal", "command line", "subprocess", "exec(", "os.system", "run command"],
    "filesystem_writes": ["write file", "overwrite", "filesystem", "file system", "save to", "create file"],
    "network_access": ["http", "https", "download", "upload", "network", "web request", "curl", "wget"],
    "credentials": ["credential", "token", "password", "private key"],
    "api_keys": ["api key", "apikey", "api_key"],
    "browser_automation": ["browser", "selenium", "playwright", "puppeteer"],
    "email": ["email", "smtp", "imap"],
    "payments": ["payment", "stripe", "invoice", "billing", "credit card"],
    "code_execution": ["execute code", "run code", "eval(", "compile", "interpreter", "code execution"],
    "database_access": ["database", "sql", "postgres", "mysql", "sqlite", "mongodb"],
    "destructive_actions": ["delete", "destroy", "drop table", "wipe", "remove all", "irreversible"],
    "deleting_files": ["delete file", "deleting files", "remove file", "rm -rf", "unlink"],
    "security_bypass": ["bypass", "disable security", "ignore ssl", "jailbreak", "exploit"],
    "scraping": ["scrape", "crawler", "crawling", "beautifulsoup", "web scraping"],
    "personal_data": ["personal data", "pii", "personally identifiable", "ssn", "social security"],
    "authentication": ["authentication", "authenticate", "oauth", "login", "session cookie"],
    "secrets": ["secret", "secrets", "secret key", "client_secret"],
}

CATEGORY_KEYWORDS = {
    "research": ["research", "paper", "literature", "citation", "arxiv"],
    "engineering": ["code", "coding", "developer", "engineering", "test", "debug", "github", "ci"],
    "security": ["security", "vulnerability", "threat", "prompt injection", "red team", "exploit"],
    "agent-infra": ["agent", "mcp", "tool", "runtime", "workflow", "orchestration", "infra"],
    "enterprise": ["enterprise", "salesforce", "crm", "erp", "compliance", "business"],
    "documents": ["document", "docx", "pdf", "pptx", "xlsx", "spreadsheet", "slide"],
    "data": ["data", "analytics", "csv", "database", "sql", "etl", "warehouse"],
    "governance": ["governance", "policy", "legal", "license", "audit", "risk"],
    "productivity": ["productivity", "todo", "calendar", "notes", "meeting", "planning"],
    "design": ["design", "figma", "ux", "ui", "image", "visual"],
    "marketing": ["marketing", "seo", "copy", "content", "social"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "unknown"


def stable_id(*parts: str) -> str:
    base = "/".join(p for p in parts if p)
    slug = slugify(parts[-1] if parts else base)
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{digest}"


def load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def write_json_array(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def upsert_records(existing: list[dict[str, Any]], new_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for record in existing + new_records:
        key = record.get("id") or record.get("skill_id") or "|".join(
            str(record.get(k, "")) for k in ("source_repo", "file_path", "source_file_path", "source_url", "raw_url", "name")
        )
        by_key[key] = record
    return sorted(by_key.values(), key=lambda r: (str(r.get("source_repo") or ""), str(r.get("source_file_path") or r.get("file_path") or ""), str(r.get("name") or "")))


def github_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "awesome-skills-library-cataloger"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_api(path_or_url: str, *, params: dict[str, Any] | None = None, raw: bool = False) -> Any:
    url = path_or_url if path_or_url.startswith("http") else "https://api.github.com" + path_or_url
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers=github_headers())
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read()
            if raw:
                return data.decode("utf-8", errors="replace")
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code} for {url}: {body[:500]}") from exc


def download_url(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=github_headers())
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not match:
        return {}, text
    frontmatter: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"\'')
        if value.startswith("[") and value.endswith("]"):
            value = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
        frontmatter[key.strip()] = value
    return frontmatter, match.group(2)


def detect_name_description(text: str, fallback_name: str = "") -> tuple[str, str]:
    frontmatter, body = extract_frontmatter(text)
    name = str(frontmatter.get("name") or frontmatter.get("title") or fallback_name or "").strip()
    description = str(frontmatter.get("description") or "").strip()
    if not name:
        heading = re.search(r"^#\s+(.+)$", body, re.M)
        name = heading.group(1).strip() if heading else fallback_name
    if not description:
        for line in body.splitlines():
            clean = line.strip().strip("# ")
            if clean and not clean.lower().startswith(("purpose", "when to use")) and len(clean) > 20:
                description = clean[:500]
                break
    return name or fallback_name or "Unknown skill", description


def risk_tags_for_text(text: str) -> list[str]:
    lower = text.lower()
    return sorted(tag for tag, needles in RISK_KEYWORDS.items() if any(needle in lower for needle in needles))


def guess_category(*values: Any) -> str:
    haystack = " ".join(json.dumps(v, ensure_ascii=False).lower() if not isinstance(v, str) else v.lower() for v in values if v)
    scores = {category: sum(1 for word in words if word in haystack) for category, words in CATEGORY_KEYWORDS.items()}
    category, score = max(scores.items(), key=lambda item: item[1])
    return category if score else "unknown"


def guess_compatibility(*values: Any) -> list[str]:
    haystack = " ".join(json.dumps(v, ensure_ascii=False).lower() if not isinstance(v, str) else v.lower() for v in values if v)
    matches: list[str] = []
    if "claude code" in haystack or "claude-code" in haystack:
        matches.append("claude_code")
    if "claude" in haystack or "skill.md" in haystack:
        matches.append("claude_skills")
    if "codex" in haystack:
        matches.append("codex")
    if "mcp" in haystack or "model context protocol" in haystack:
        matches.append("mcp")
    if "openclaw" in haystack:
        matches.append("openclaw")
    if not matches:
        matches.append("generic_agents")
    return matches


def redistribution_status(license_spdx: str | None, license_name: str | None, path: str = "", notes: str = "") -> str:
    spdx = (license_spdx or "").strip()
    lower = f"{spdx} {license_name or ''} {path} {notes}".lower()
    folder = Path(path).parts[-2].lower() if len(Path(path).parts) >= 2 else Path(path).stem.lower()
    if folder in SOURCE_AVAILABLE_DOCUMENT_SKILLS or "source-available" in lower or "source available" in lower:
        return "index_only"
    if "proprietary" in lower or "all rights reserved" in lower:
        return "prohibited"
    if spdx in ALLOWED_LICENSES:
        return "attribution_required"
    if spdx in PUBLIC_DOMAIN_LICENSES:
        return "allowed"
    if spdx in GPL_FAMILY_LICENSES or spdx.startswith(("GPL", "LGPL", "AGPL")):
        return "manual_review"
    if not spdx or spdx.upper() == "NOASSERTION" or spdx.upper() == "NONE":
        return "index_only"
    return "unknown"


def is_copy_allowed(license_spdx: str | None, license_name: str | None, path: str = "", notes: str = "") -> bool:
    return redistribution_status(license_spdx, license_name, path, notes) in {"allowed", "attribution_required"}


def decode_github_content(item: dict[str, Any]) -> str:
    content = item.get("content", "")
    encoding = item.get("encoding")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")
    return str(content)


def yaml_scalar(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    if not text or any(ch in text for ch in ":#[]{}\n") or text.strip() != text:
        return json.dumps(text)
    return text


def write_simple_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {yaml_scalar(item)}")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        data[key.strip()] = str(value)
    return data


def safe_copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store")
    shutil.copytree(src, dst, ignore=ignore)


def copy_github_folder(owner: str, repo: str, ref: str, folder_path: str, destination: Path) -> None:
    """Download a GitHub tarball and copy one folder without executing content."""
    folder_path = folder_path.strip("/")
    tar_url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{ref}"
    with tempfile.TemporaryDirectory(prefix="skill-import-") as temp_name:
        temp_dir = Path(temp_name)
        archive = temp_dir / "repo.tar.gz"
        download_url(tar_url, archive)
        extract_dir = temp_dir / "extract"
        extract_dir.mkdir()
        with tarfile.open(archive, "r:gz") as tar:
            for member in tar.getmembers():
                target = (extract_dir / member.name).resolve()
                if not str(target).startswith(str(extract_dir.resolve())):
                    raise RuntimeError(f"Unsafe archive path: {member.name}")
            tar.extractall(extract_dir)
        roots = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not roots:
            raise RuntimeError("Downloaded repository archive was empty")
        source_folder = roots[0] / folder_path
        if not source_folder.exists() or not source_folder.is_dir():
            raise RuntimeError(f"Skill folder not found in archive: {folder_path}")
        safe_copy_tree(source_folder, destination)
