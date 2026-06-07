#!/usr/bin/env python3
"""Validate Awesome Skills Library skill packages without external dependencies."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REQUIRED_PACKAGE_FILES = [
    "SKILL.md",
    "skill.yaml",
    "tests/basic.yaml",
    "examples/input.md",
    "examples/output.md",
]
REQUIRED_FIELDS = [
    "id",
    "name",
    "version",
    "category",
    "description",
    "use_cases",
    "inputs",
    "outputs",
    "required_tools",
    "permissions",
    "safety_level",
    "risk_tags",
    "compatibility",
    "provenance",
    "license",
    "maintainers",
    "tests",
]
PERMISSION_FIELDS = ["network", "filesystem", "code_execution", "external_api", "user_data_access"]
COMPATIBILITY_FIELDS = ["generic_agents", "claude_skills", "chatgpt_skills", "mcp", "nanda_agentfacts"]
COMPATIBILITY_STATUSES = {"supported", "experimental", "not_supported", "unknown"}
SAFETY_LEVELS = {"low", "medium", "high"}
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class YamlParseError(ValueError):
    """Raised when the limited YAML parser cannot parse a metadata file."""


@dataclass
class CheckReport:
    label: str
    passed: bool
    details: list[str] = field(default_factory=list)


@dataclass
class SkillReport:
    path: Path
    skill_id: str
    checks: list[CheckReport] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def parse_scalar(value: str) -> Any:
    """Parse the YAML scalar forms used in skill metadata."""
    value = value.strip()
    if value == "[]":
        return []
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a conservative subset of YAML sufficient for repository metadata files."""
    lines: list[tuple[int, str, int]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise YamlParseError(f"line {line_no}: tabs are not supported for indentation")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lines.append((indent, raw_line.strip(), line_no))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        current_indent, content, _ = lines[index]
        if current_indent < indent:
            return {}, index
        if current_indent > indent:
            raise YamlParseError(f"line {lines[index][2]}: unexpected indentation")
        if content.startswith("- "):
            return parse_list(index, indent)
        return parse_map(index, indent)

    def parse_map(index: int, indent: int) -> tuple[dict[str, Any], int]:
        result: dict[str, Any] = {}
        while index < len(lines):
            current_indent, content, line_no = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise YamlParseError(f"line {line_no}: unexpected indentation")
            if content.startswith("- "):
                break
            if ":" not in content:
                raise YamlParseError(f"line {line_no}: expected 'key: value'")
            key, value = content.split(":", 1)
            key = key.strip()
            if not key:
                raise YamlParseError(f"line {line_no}: empty keys are not supported")
            if key in result:
                raise YamlParseError(f"line {line_no}: duplicate key '{key}'")
            value = value.strip()
            index += 1
            if value:
                result[key] = parse_scalar(value)
            elif index < len(lines) and lines[index][0] > current_indent:
                result[key], index = parse_block(index, lines[index][0])
            else:
                result[key] = None
        return result, index

    def parse_list(index: int, indent: int) -> tuple[list[Any], int]:
        result: list[Any] = []
        while index < len(lines):
            current_indent, content, line_no = lines[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise YamlParseError(f"line {line_no}: unexpected indentation")
            if not content.startswith("- "):
                break
            item = content[2:].strip()
            index += 1
            if not item:
                value, index = parse_block(index, indent + 2)
                result.append(value)
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_-]*\s*:", item) and not item.startswith(("\'", '"')):
                key, raw_value = item.split(":", 1)
                item_map: dict[str, Any] = {}
                raw_value = raw_value.strip()
                if raw_value:
                    item_map[key.strip()] = parse_scalar(raw_value)
                elif index < len(lines) and lines[index][0] > current_indent:
                    item_map[key.strip()], index = parse_block(index, lines[index][0])
                else:
                    item_map[key.strip()] = None
                if index < len(lines) and lines[index][0] > current_indent:
                    continuation, index = parse_map(index, lines[index][0])
                    item_map.update(continuation)
                result.append(item_map)
            else:
                result.append(parse_scalar(item))
        return result, index

    parsed, final_index = parse_block(0, 0)
    if final_index != len(lines):
        raise YamlParseError(f"line {lines[final_index][2]}: could not parse remaining content")
    if not isinstance(parsed, dict):
        raise YamlParseError("document root must be a mapping")
    return parsed


def find_skill_dirs() -> list[Path]:
    if not SKILLS_DIR.exists():
        return []
    return sorted(path.parent for path in SKILLS_DIR.rglob("skill.yaml"))


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_named_descriptions(metadata: dict[str, Any], field_name: str, errors: list[str]) -> None:
    values = metadata.get(field_name)
    if not isinstance(values, list) or not values:
        errors.append(f"{field_name} must be a non-empty list")
        return
    for index, item in enumerate(values, start=1):
        if not isinstance(item, dict):
            errors.append(f"{field_name}[{index}] must be an object with name and description")
            continue
        for key in sorted(set(item) - {"name", "description"}):
            errors.append(f"{field_name}[{index}].{key} is not supported")
        if not non_empty_string(item.get("name")):
            errors.append(f"{field_name}[{index}].name must be a non-empty string")
        if not non_empty_string(item.get("description")):
            errors.append(f"{field_name}[{index}].description must be a non-empty string")


def validate_string_list(
    metadata: dict[str, Any],
    field_name: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
    require_unique: bool = False,
) -> None:
    values = metadata.get(field_name)
    if not isinstance(values, list) or (not values and not allow_empty):
        errors.append(f"{field_name} must be a {'possibly empty ' if allow_empty else 'non-empty '}list")
        return
    seen: set[str] = set()
    for index, item in enumerate(values, start=1):
        if not non_empty_string(item):
            errors.append(f"{field_name}[{index}] must be a non-empty string")
        elif require_unique:
            if item in seen:
                errors.append(f"{field_name}[{index}] duplicates an earlier value: {item}")
            seen.add(item)


def validate_metadata(metadata: dict[str, Any], skill_dir: Path) -> list[str]:
    errors: list[str] = []

    for field_name in REQUIRED_FIELDS:
        if field_name not in metadata:
            errors.append(f"missing metadata field: {field_name}")
    for field_name in sorted(set(metadata) - set(REQUIRED_FIELDS)):
        errors.append(f"unsupported metadata field: {field_name}")

    skill_id = metadata.get("id")
    if not non_empty_string(skill_id):
        errors.append("id must be a non-empty string")
    elif not ID_PATTERN.fullmatch(skill_id):
        errors.append("id must use dot format with lowercase alphanumeric or hyphenated segments, e.g. agent-infra.agentfacts-profile")

    version = metadata.get("version")
    if not non_empty_string(version):
        errors.append("version must be a non-empty string")
    elif not SEMVER_PATTERN.fullmatch(version):
        errors.append("version must follow semantic versioning, e.g. 0.1.0")

    for field_name in ["name", "category", "description", "license"]:
        if field_name in metadata and not non_empty_string(metadata[field_name]):
            errors.append(f"{field_name} must be a non-empty string")

    validate_string_list(metadata, "use_cases", errors)
    validate_named_descriptions(metadata, "inputs", errors)
    validate_named_descriptions(metadata, "outputs", errors)
    validate_string_list(metadata, "required_tools", errors, allow_empty=True, require_unique=True)
    validate_string_list(metadata, "risk_tags", errors, allow_empty=True, require_unique=True)

    permissions = metadata.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("permissions must be an object")
    else:
        for permission in PERMISSION_FIELDS:
            if permission not in permissions:
                errors.append(f"permissions.{permission} is required")
            elif not isinstance(permissions[permission], bool):
                errors.append(f"permissions.{permission} must be true or false")
        for permission in sorted(set(permissions) - set(PERMISSION_FIELDS)):
            errors.append(f"permissions.{permission} is not a supported permission")

    safety_level = metadata.get("safety_level")
    if safety_level not in SAFETY_LEVELS:
        errors.append("safety_level must be one of: low, medium, high")

    compatibility = metadata.get("compatibility")
    if not isinstance(compatibility, dict):
        errors.append("compatibility must be an object")
    else:
        for field_name in COMPATIBILITY_FIELDS:
            if field_name not in compatibility:
                errors.append(f"compatibility.{field_name} is required")
            elif compatibility[field_name] not in COMPATIBILITY_STATUSES:
                errors.append(
                    f"compatibility.{field_name} must be one of: "
                    f"{', '.join(sorted(COMPATIBILITY_STATUSES))}"
                )
        for field_name in sorted(set(compatibility) - set(COMPATIBILITY_FIELDS)):
            errors.append(f"compatibility.{field_name} is not a supported compatibility target")

    provenance = metadata.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        for field_name in ["author", "source"]:
            if not non_empty_string(provenance.get(field_name)):
                errors.append(f"provenance.{field_name} must be a non-empty string")
        references = provenance.get("references")
        if not isinstance(references, list):
            errors.append("provenance.references must be a list")
        else:
            for index, reference in enumerate(references, start=1):
                if not non_empty_string(reference):
                    errors.append(f"provenance.references[{index}] must be a non-empty string")

    maintainers = metadata.get("maintainers")
    if not isinstance(maintainers, list) or not maintainers:
        errors.append("maintainers must be a non-empty list")
    else:
        for index, maintainer in enumerate(maintainers, start=1):
            if not isinstance(maintainer, dict):
                errors.append(f"maintainers[{index}] must be an object with name and contact")
                continue
            for key in sorted(set(maintainer) - {"name", "contact"}):
                errors.append(f"maintainers[{index}].{key} is not supported")
            if not non_empty_string(maintainer.get("name")):
                errors.append(f"maintainers[{index}].name must be a non-empty string")
            if not non_empty_string(maintainer.get("contact")):
                errors.append(f"maintainers[{index}].contact must be a non-empty string")

    tests = metadata.get("tests")
    if not isinstance(tests, list) or not tests:
        errors.append("tests must be a non-empty list")
    else:
        seen_tests: set[str] = set()
        for index, test_file in enumerate(tests, start=1):
            if not non_empty_string(test_file):
                errors.append(f"tests[{index}] must be a non-empty string path")
            else:
                if test_file in seen_tests:
                    errors.append(f"tests[{index}] duplicates an earlier test path: {test_file}")
                seen_tests.add(test_file)
                if not (skill_dir / test_file).exists():
                    errors.append(f"listed test file does not exist: {test_file}")

    return errors


def validate_skill(skill_dir: Path) -> tuple[str | None, list[CheckReport]]:
    checks: list[CheckReport] = []

    for required_file in REQUIRED_PACKAGE_FILES:
        exists = (skill_dir / required_file).exists()
        label = f"{required_file} found"
        checks.append(CheckReport(label=label, passed=exists, details=[] if exists else [f"missing {required_file}"]))

    metadata_path = skill_dir / "skill.yaml"
    skill_id: str | None = None
    metadata_errors: list[str] = []
    if metadata_path.exists():
        try:
            metadata = load_yaml(metadata_path)
            parsed_id = metadata.get("id")
            if isinstance(parsed_id, str):
                skill_id = parsed_id
            metadata_errors.extend(validate_metadata(metadata, skill_dir))
        except YamlParseError as exc:
            metadata_errors.append(f"could not parse skill.yaml: {exc}")
    if metadata_errors:
        checks.append(CheckReport(label="metadata fields valid", passed=False, details=metadata_errors))
    else:
        checks.append(CheckReport(label="skill.yaml valid", passed=metadata_path.exists()))

    return skill_id, checks


def main() -> int:
    print("Validating Awesome Skills Library...\n")

    skill_dirs = find_skill_dirs()
    if not skill_dirs:
        print("No skills found under skills/.")
        print("\nSummary:")
        print("0 skills checked")
        print("0 passed")
        print("1 failed")
        return 1

    reports: list[SkillReport] = []
    seen_ids: dict[str, Path] = {}

    for skill_dir in skill_dirs:
        skill_id, checks = validate_skill(skill_dir)
        display_name = skill_id or str(skill_dir.relative_to(ROOT))
        report = SkillReport(path=skill_dir, skill_id=display_name, checks=checks)
        if skill_id:
            if skill_id in seen_ids:
                duplicate_path = seen_ids[skill_id].relative_to(ROOT)
                report.checks.append(
                    CheckReport(
                        label="skill id unique",
                        passed=False,
                        details=[f"duplicate skill id also used by {duplicate_path}"],
                    )
                )
            else:
                seen_ids[skill_id] = skill_dir
                report.checks.append(CheckReport(label="skill id unique", passed=True))
        else:
            report.checks.append(CheckReport(label="skill id unique", passed=False, details=["cannot check duplicate id without a valid id"]))
        reports.append(report)

    for report in reports:
        prefix = "✓" if report.passed else "✗"
        print(f"{prefix} {report.skill_id}")
        for check in report.checks:
            check_prefix = "✓" if check.passed else "✗"
            print(f"  {check_prefix} {check.label}")
            for detail in check.details:
                print(f"    - {detail}")
        print()

    passed_count = sum(1 for report in reports if report.passed)
    failed_count = len(reports) - passed_count
    print("Summary:")
    print(f"{len(reports)} skill{'s' if len(reports) != 1 else ''} checked")
    print(f"{passed_count} passed")
    print(f"{failed_count} failed")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
