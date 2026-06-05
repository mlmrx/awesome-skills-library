# Skill Metadata Schema

The canonical machine-readable schema is `schema/skill.schema.json`. The initial validator checks required top-level fields without external dependencies.

## Required fields

- `id`: stable unique identifier, usually `<category>.<skill-slug>`.
- `name`: human-readable skill name.
- `version`: semantic version for the skill package.
- `category`: registry category.
- `description`: short description of the capability.
- `use_cases`: recurring tasks the skill supports.
- `inputs`: required or optional inputs.
- `outputs`: expected outputs.
- `required_tools`: tools the skill may need.
- `permissions`: permissions the skill may request.
- `safety_level`: low, medium, high, or critical.
- `risk_tags`: risk categories relevant to the skill.
- `compatibility`: agent runtimes or environments where the skill is expected to work.
- `provenance`: source and review information.
- `license`: license for the skill package.
- `maintainers`: maintainers or contact handles.
- `tests`: test files associated with the skill.

## Compatibility with YAML tooling

The repository currently avoids mandatory dependencies. Scripts use a small parser for top-level YAML fields and simple lists/maps. Future versions may adopt a dedicated YAML parser if the validation requirements justify it.
