# Awesome Skills Library

A public catalog of reusable **skills**: small, self-contained instruction
packs that teach an AI coding agent how to do a focused job well.

## First 30 seconds

### What is this?

This repository collects community-maintained skills. Each skill lives in its own
directory and includes a `SKILL.md` file with the instructions, workflow,
examples, and assets needed to perform one task.

### Why does it matter?

Skills make agent workflows easier to share, review, and reuse. Instead of
copying long prompts between projects, contributors can publish a tested skill
once and others can install or adapt it.

### How do I browse skills?

Browse the repository folders on GitHub. Skills are organized by directory; open
a skill's `SKILL.md` to see what it does, when to use it, and any supporting
files it needs.

### How do I add a skill?

1. Create a focused skill directory under the appropriate collection folder.
2. Add a `SKILL.md` that explains the trigger, workflow, inputs, outputs, and
   validation steps.
3. Include only supporting files the skill needs, such as examples, templates,
   scripts, or assets.
4. Open a pull request using the checklist in [CONTRIBUTING.md](CONTRIBUTING.md).

### How do I validate my contribution?

Before opening a pull request:

```bash
find . -name SKILL.md -print
```

Then review your changed skill manually:

- The skill has one clear purpose.
- `SKILL.md` explains when to use it and when not to use it.
- Any referenced files, scripts, or assets exist in the skill directory.
- Examples are short and safe to run.
- No secrets, credentials, private data, or copyrighted material were added
  without permission.

## What makes a good skill?

A good skill is:

- **Specific**: it handles one repeatable workflow, not an entire discipline.
- **Actionable**: it gives clear steps, decision points, and expected outputs.
- **Portable**: it avoids assumptions about one private environment unless those
  assumptions are documented.
- **Testable**: it includes a practical way to check that the skill works.
- **Maintainable**: it keeps examples and support files minimal.

## License

This project is released under [CC0 1.0 Universal](LICENSE). By contributing,
you agree that your contribution is provided under the same license.
Awesome Skills Library is an open-source package index for reusable AI agent skills.

A skill is **a reusable AI agent capability package containing instructions, metadata, examples, tests, safety boundaries, and compatibility information.**

> Prompts describe intent. Tools expose actions. Skills encode repeatable know-how into reusable agent capabilities.

This repository is the public-launch foundation for a contributor-friendly skills registry. It is intentionally small: no website, no heavy framework, and no product surface beyond the repository, schema, templates, validation scripts, and one complete example skill.

## Why skills matter for AI agents

AI agents increasingly need repeatable procedures rather than one-off prompts. A well-designed skill helps an agent:

- perform a bounded task consistently;
- understand required inputs and expected outputs;
- know what tools or permissions may be needed;
- apply safety and quality constraints before acting;
- expose compatibility information for different agent runtimes;
- give maintainers a testable unit that can improve over time.

Skills make operational knowledge portable. They let researchers, agent builders, and infrastructure teams share a capability without forcing every agent stack to rediscover the same workflow.

## Not a prompt library

Awesome Skills Library is not a prompt dump. Prompt snippets are usually informal text fragments. A skill package is structured infrastructure:

- agent-facing instructions in `SKILL.md`;
- machine-readable metadata in `skill.yaml`;
- examples that show realistic inputs and outputs;
- tests that define minimum expected behavior;
- safety boundaries and failure modes;
- compatibility and provenance information.

The goal is not to collect clever wording. The goal is to make useful agent capabilities discoverable, reusable, reviewable, and maintainable.

## What every skill package contains

Every skill must include:

```text
SKILL.md
skill.yaml
tests/basic.yaml
examples/input.md
examples/output.md
```

`SKILL.md` must include these sections:

- Purpose
- When to use this skill
- Required inputs
- Step-by-step workflow
- Output format
- Quality bar
- Safety boundaries
- Failure modes

`skill.yaml` must include these fields:

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

See [`docs/schema.md`](docs/schema.md) and [`schema/skill.schema.json`](schema/skill.schema.json) for the current metadata contract.

## Repository structure

```text
.github/                 GitHub Actions, issue templates, and PR template
docs/                    Project vision, schema notes, safety, roadmap, and compatibility guidance
schema/                  Machine-readable skill metadata schema
templates/skill/         Starting point for new skills
skills/                  Published skill packages, grouped by category
registry/                Registry data generated or maintained from skill metadata
scripts/                 Lightweight maintenance scripts
tests/fixtures/          Test fixtures for future script and registry tests
SKILLS_INDEX.md          Human-readable generated index of skills
```

## Add a new skill

1. Create a skill from the template:

   ```bash
   python scripts/new_skill.py <category>/<skill-slug>
   ```

   Example:

   ```bash
   python scripts/new_skill.py security/prompt-injection-review
   ```

2. Edit the generated files:
   - complete `SKILL.md` with a concrete workflow;
   - complete `skill.yaml` with stable metadata;
   - update `tests/basic.yaml` with expected behavior;
   - add realistic `examples/input.md` and `examples/output.md`.

3. Validate locally:

   ```bash
   python scripts/validate_skills.py
   ```

4. Regenerate the index:

   ```bash
   python scripts/generate_index.py
   ```

5. Open a pull request using the checklist in `.github/pull_request_template.md`.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contributor workflow.

## Validate skills locally

This project uses only Python standard-library scripts for the initial repository foundation.

```bash
python scripts/validate_skills.py
python scripts/generate_index.py
```

`validate_skills.py` scans `skills/`, checks required files, validates schema v1 metadata fields and enum values, verifies listed test files, detects duplicate skill IDs, prints a grouped pass/fail report, and exits non-zero on failure.

`generate_index.py` reads all `skill.yaml` files and writes [`SKILLS_INDEX.md`](SKILLS_INDEX.md), grouped by category.

## Initial roadmap

The first milestones are intentionally practical:

1. Establish the public repository structure, schema, and contribution process.
2. Add a small set of high-quality skills across agent infrastructure, safety, research, and developer workflows.
3. Improve validation coverage while keeping dependencies minimal.
4. Expand compatibility metadata for common agent runtimes and execution environments.
5. Define registry publishing conventions once the skill set is large enough to justify automation.

See [`docs/roadmap.md`](docs/roadmap.md) for more detail.

## How contributors can help

Useful contributions include:

- proposing reusable skills with clear tests and safety boundaries;
- improving existing skill workflows, examples, or metadata;
- adding compatibility notes for agent runtimes;
- identifying safety risks or ambiguous instructions;
- improving validation scripts without adding unnecessary dependencies;
- reviewing whether a proposed skill is reusable infrastructure rather than a one-off prompt.

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md), and [`SECURITY.md`](SECURITY.md) before contributing.

## Cataloging existing skills

Awesome Skills Library uses an attribution-first discovery pipeline for public AI agent skills. The catalog scripts index metadata, source URLs, repository details, license information, and risk notes before any third-party content is considered for import. This protects original creators, preserves license context, and prevents accidental redistribution of source-available or unknown-license materials.

Discovery and import outputs are written under `catalog/`:

- `catalog/sources.yaml` lists configured starting sources.
- `catalog/discovered-skills.jsonl` stores append-friendly discovery records.
- `catalog/discovered-skills.json` stores normalized searchable catalog records.
- `catalog/attribution.json` preserves source, author, license, and redistribution status.
- `catalog/import-report.md` summarizes review queues, risk flags, licenses, and duplicates.

Run the pipeline with:

```bash
export GITHUB_TOKEN=your_token_here

python scripts/import_anthropic_skills.py
python scripts/discover_github_skills.py --max-results 500
python scripts/normalize_discovered_skills.py
python scripts/generate_import_report.py
```

`GITHUB_TOKEN` is optional, but authenticated GitHub API requests have higher rate limits. The discovery script does not clone repositories or download whole projects; it fetches repository metadata and candidate `SKILL.md` files only when needed for metadata extraction and risk tagging.

Anthropic's official skills repository is indexed separately because it contains mixed licensing. Source-available document skills such as `docx`, `pdf`, `pptx`, and `xlsx` are cataloged with attribution and license notes, but must not be copied into `skills/` unless redistribution permission is explicitly confirmed. Unknown-license community skills are also index-only until manual review. See [`sources/README.md`](sources/README.md) for the attribution and manual-review rules.

## License

This repository is released under the terms in [`LICENSE`](LICENSE).
