# Compatibility

Compatibility metadata helps users decide whether a skill can be used in their agent runtime without rewriting it.

## Recommended compatibility fields

- `agent_runtimes`: runtimes where the instructions are expected to work.
- `tool_requirements`: tools needed by the skill, if any.
- `model_requirements`: model capabilities assumed by the skill.
- `permissions_required`: filesystem, network, shell, browser, or external service access.
- `known_limitations`: environments where the skill is untested or unsuitable.

## Guidance

Be conservative. It is better to say a skill is untested than to imply broad support. Compatibility claims should come from successful use, tests, or careful review.
