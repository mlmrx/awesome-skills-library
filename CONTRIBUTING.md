# Contributing to Awesome Skills Library

Thank you for helping build reusable AI agent infrastructure. Contributions should make skills easier to discover, evaluate, run, and maintain.

## What belongs here

A contribution belongs in this repository when it describes a repeatable AI agent capability that can be reused across tasks, teams, or agent runtimes.

A contribution does **not** belong here if it is only:

- a single prompt with no metadata, tests, or safety boundaries;
- a private workflow that depends on unavailable internal systems;
- a vague best-practices note without an operational procedure;
- a tool wrapper without agent-facing know-how.

## Required skill package files

Every skill must include:

```text
SKILL.md
skill.yaml
tests/basic.yaml
examples/input.md
examples/output.md
```

## Create a skill from the template

Run:

```bash
python scripts/new_skill.py <category>/<skill-slug>
```

Example:

```bash
python scripts/new_skill.py security/prompt-injection-review
```

The script creates `skills/<category>/<skill-slug>/` from `templates/skill/` and refuses to overwrite an existing skill unless `--force` is passed.

## Complete `SKILL.md`

`SKILL.md` must include:

- Purpose
- When to use this skill
- Required inputs
- Step-by-step workflow
- Output format
- Quality bar
- Safety boundaries
- Failure modes

Write for an AI agent that must perform the task reliably. Be concrete. Include decision points, constraints, and failure handling.

## Complete `skill.yaml`

`skill.yaml` must include:

- `id`
- `name`
- `version`
- `category`
- `description`
- `use_cases`
- `inputs`
- `outputs`
- `required_tools`
- `permissions`
- `safety_level`
- `risk_tags`
- `compatibility`
- `provenance`
- `license`
- `maintainers`
- `tests`

Use stable, lowercase skill IDs such as `security.prompt-injection-review` or `agent-infra.agentfacts-profile`.

## Add tests and examples

At minimum, `tests/basic.yaml` should describe:

- a realistic input;
- expected output properties;
- checks for required sections or behavior;
- any safety or refusal expectations.

Examples should be short but realistic. `examples/input.md` should show what a user or system might provide. `examples/output.md` should show the expected shape and level of detail.

## Validate before opening a pull request

Run:

```bash
python scripts/validate_skills.py
python scripts/generate_index.py
```

Commit the generated `SKILLS_INDEX.md` when skill metadata changes.

## Pull request expectations

A good pull request includes:

- a clear description of what changed;
- a skill checklist if adding or changing a skill;
- local validation results;
- risk level and safety notes;
- reviewer notes for ambiguous design decisions.

## Review principles

Reviewers should ask:

- Is this skill reusable beyond one task or organization?
- Are the required inputs and outputs explicit?
- Are safety boundaries concrete?
- Can the basic test catch obvious regressions?
- Is compatibility information honest and useful?
