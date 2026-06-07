# Compatibility

Compatibility metadata helps users decide whether a skill can be used in their agent runtime without rewriting it.

## Schema v1 compatibility targets

Every `skill.yaml` must declare a status for these targets:

- `generic_agents`: instruction-following agents that can read `SKILL.md` and produce the declared outputs.
- `claude_skills`: Claude-style skill package environments.
- `chatgpt_skills`: ChatGPT-style skill package environments.
- `mcp`: Model Context Protocol servers, tools, or resource integrations.
- `nanda_agentfacts`: NANDA / AgentFacts-style registry or profile workflows.

Each target must use one of these values:

- `supported`: expected to work in this environment with the current package.
- `experimental`: plausible support exists, but more testing or packaging work is needed.
- `not_supported`: the skill is not designed for this environment.
- `unknown`: maintainers have not evaluated this environment yet.

Example:

```yaml
compatibility:
  generic_agents: supported
  claude_skills: experimental
  chatgpt_skills: experimental
  mcp: not_supported
  nanda_agentfacts: experimental
```

## Guidance

Be conservative. It is better to say `unknown` or `experimental` than to imply broad support. Compatibility claims should come from successful use, tests, or careful review.

Use `not_supported` when a target is out of scope for the package as written. For example, a Markdown-only instruction skill should generally mark `mcp` as `not_supported` until it includes an actual MCP server, tool contract, or resource definition.
