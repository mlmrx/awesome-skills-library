# Skill Metadata Schema

The canonical machine-readable schema is `schema/skill.schema.json`. Schema v1 makes every skill package registry-ready by requiring structured metadata, explicit permissions, compatibility status, provenance, maintainers, and test references.

## Required package files

A valid skill package is a directory under `skills/` containing:

- `SKILL.md`: reusable agent instructions.
- `skill.yaml`: metadata conforming to schema v1.
- `tests/basic.yaml`: baseline validation scenario.
- `examples/input.md`: representative input.
- `examples/output.md`: representative expected output.

## Required metadata fields

- `id`: stable unique identifier in dot format, for example `agent-infra.agentfacts-profile`. Segments should use lowercase letters, numbers, and hyphens.
- `name`: human-readable skill name.
- `version`: semantic version for the skill package, for example `0.1.0`.
- `category`: registry category.
- `description`: short description of the reusable capability.
- `use_cases`: non-empty list of recurring tasks the skill supports.
- `inputs`: non-empty list of input objects with `name` and `description`.
- `outputs`: non-empty list of output objects with `name` and `description`.
- `required_tools`: list of required tools, or `none` when no tools are required.
- `permissions`: object with explicit boolean values for `network`, `filesystem`, `code_execution`, `external_api`, and `user_data_access`.
- `safety_level`: one of `low`, `medium`, or `high`.
- `risk_tags`: list of relevant risk categories.
- `compatibility`: object declaring support status for `generic_agents`, `claude_skills`, `chatgpt_skills`, `mcp`, and `nanda_agentfacts`.
- `provenance`: object with `author`, `source`, and `references`.
- `license`: license for the skill package.
- `maintainers`: non-empty list of maintainer objects with `name` and `contact`.
- `tests`: non-empty list of test file paths relative to the skill directory.

## Compatibility statuses

Each compatibility target must use one of these values:

- `supported`: expected to work in the target environment.
- `experimental`: plausible support, but not yet mature or fully verified.
- `not_supported`: not designed for the target environment.
- `unknown`: compatibility has not been evaluated.

## Permission model

Permissions must be explicit booleans so reviewers can understand what a skill may need before running it:

```yaml
permissions:
  network: false
  filesystem: false
  code_execution: false
  external_api: false
  user_data_access: false
```

## Validation

Run the local validator before submitting a skill:

```bash
python scripts/validate_skills.py
```

The validator recursively scans `skills/`, finds every directory containing `skill.yaml`, checks required package files, validates schema v1 metadata rules, detects duplicate skill IDs, and verifies that listed test files exist.

## Compatibility with YAML tooling

The repository currently avoids mandatory runtime dependencies. `scripts/validate_skills.py` includes a conservative YAML parser for the subset used by skill metadata. Keep metadata simple: top-level mappings, nested mappings, lists, strings, booleans, and empty lists such as `references: []`.
