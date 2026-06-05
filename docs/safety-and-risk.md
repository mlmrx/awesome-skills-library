# Safety and Risk

Skills can influence how agents use tools, interpret inputs, and produce outputs. Every skill should document safety boundaries in the same package as the workflow.

## Safety levels

- `low`: informational or formatting tasks with limited risk.
- `medium`: tasks that may affect decisions, reputations, or user trust.
- `high`: tasks involving sensitive data, security, finances, legal, medical, or privileged systems.
- `critical`: tasks that could cause severe harm if misused and require strict review before inclusion.

## Risk tags

Use risk tags to make concerns searchable. Examples:

- `misrepresentation`
- `privacy`
- `security`
- `prompt-injection`
- `external-action`
- `regulated-domain`
- `human-review-required`

## Human review

Skills should recommend human review when outputs make trust claims, affect user safety, summarize sensitive evidence, or could be mistaken for authoritative certification.
