# Contributing

Thanks for helping build the Awesome Skills Library. This guide keeps
contributions easy to review and easy for others to reuse.

## Contributor path

1. **Check the existing library**: avoid adding a duplicate skill. If a similar
   skill exists, improve it instead.
2. **Pick one workflow**: a skill should solve one focused problem with a clear
   trigger and output.
3. **Create or update the skill**: write the instructions in `SKILL.md` and keep
   supporting files next to the skill.
4. **Validate the contribution**: run the checks below and manually review the
   skill.
5. **Open a pull request**: describe what changed, why it belongs here, and how
   you validated it.

## Skill requirements

Every skill must include a `SKILL.md` file. Keep it concise and include:

- **Purpose**: what the skill helps an agent do.
- **Use when**: the situations that should trigger the skill.
- **Do not use when**: nearby cases where the skill is the wrong tool.
- **Inputs**: files, credentials, context, or user details the skill expects.
- **Workflow**: the steps the agent should follow.
- **Outputs**: what the agent should produce or change.
- **Validation**: commands, review steps, or examples that prove the skill works.

Supporting files are welcome when they make the skill easier to use. Keep them
minimal and reference them from `SKILL.md`.

## Validation checklist

Run this command from the repository root to confirm the repository can find
skill entry points:

```bash
find . -name SKILL.md -print
```

Then check your changed files:

- `SKILL.md` is present in each new skill directory.
- Links and file references in `SKILL.md` resolve correctly.
- Commands or scripts in the skill are safe and documented.
- Examples do not require private services unless clearly marked optional.
- The contribution does not include secrets, tokens, private customer data, or
  unlicensed third-party content.
- The skill is written for reuse by many projects, not only one internal setup.

## Pull request checklist

In your pull request, include:

- A short summary of the new or changed skill.
- The problem it solves and who should use it.
- The validation you performed.
- Any known limitations or follow-up work.

## Review expectations

Maintainers may ask you to narrow the scope, clarify triggers, remove
unnecessary files, or add validation. Small, focused pull requests are reviewed
faster than broad collections of unrelated skills.
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
