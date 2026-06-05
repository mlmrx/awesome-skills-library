# AgentFacts Profile

## Purpose

Create an AgentFacts-style profile for another AI agent. The profile should make the agent's identity, operator, purpose, capabilities, contracts, trust claims, verification metadata, and risks explicit for review.

This skill does not certify the target agent. It organizes available information into a structured profile and identifies claims that require verification or human review.

## When to use this skill

Use this skill when a user asks for a transparent profile of an AI agent, assistant, bot, automation service, or agent-like system. It is especially useful before integrating an agent into a workflow, listing it in a registry, comparing agents, or evaluating whether its claims are sufficiently documented.

Do not use this skill as a substitute for a security audit, legal review, model evaluation, or formal certification.

## Required inputs

- Target agent name or identifier.
- Available description of the target agent.
- Owner, operator, or publisher information if available.
- Stated purpose or deployment context.
- Known capabilities and limitations.
- Input and output expectations.
- Evidence for trust, safety, security, privacy, or compliance claims.
- Any known incidents, open questions, or risk concerns.

If any required input is missing, mark it as `unknown` and list it under verification gaps rather than inventing details.

## Step-by-step workflow

1. Identify the target agent and separate verified facts from user-provided claims.
2. Extract owner, operator, publisher, or maintainer information. If these differ, preserve the distinction.
3. Summarize the agent's stated purpose and the environment where it is expected to operate.
4. List capabilities as bounded statements. Avoid broad claims such as "can do anything" or "fully secure".
5. Define the input contract: accepted inputs, required context, rejected inputs, and assumptions.
6. Define the output contract: output types, structure, quality expectations, and known limitations.
7. Record trust claims with supporting evidence. Mark unsupported claims as unverified.
8. Add verification metadata, including evidence sources, review date if provided, evaluator identity if provided, and confidence level.
9. Identify risk notes, including privacy, security, autonomy, external actions, user reliance, and misrepresentation concerns.
10. Recommend whether human review is required before relying on the profile or integrating the target agent.
11. Produce the profile in the required output format and include verification gaps.

## Output format

Return a Markdown profile with these sections:

```markdown
# AgentFacts Profile: <agent name>

## Identity
## Owner / Operator
## Purpose
## Capabilities
## Input Contract
## Output Contract
## Trust Claims
## Verification Metadata
## Risk Notes
## Human Review Recommendation
## Verification Gaps
```

Use `unknown` for missing information. Label each trust claim as `verified`, `partially verified`, `self-asserted`, or `unverified` based only on the supplied evidence.

## Quality bar

- The profile distinguishes facts, claims, assumptions, and unknowns.
- Capabilities are specific and bounded.
- Input and output contracts are operational enough for an integrator to evaluate.
- Trust claims are tied to evidence or explicitly marked unverified.
- Risk notes are concrete and proportional to the provided information.
- The human review recommendation explains what should be reviewed and why.

## Safety boundaries

- Do not invent ownership, certifications, audits, benchmark results, or compliance status.
- Do not present the profile as an endorsement, certification, or security audit.
- Do not remove material uncertainty to make the target agent look safer or more capable.
- Do not include secrets, private keys, personal data, or confidential internal details unless the user has explicitly provided them for review and they are necessary to summarize at a high level.
- Recommend human review when the agent can take external actions, handle sensitive data, make trust claims, or influence consequential decisions.

## Failure modes

- Insufficient source information: produce a partial profile and list verification gaps.
- Conflicting claims: preserve the conflict and identify what evidence would resolve it.
- Unsupported trust claims: mark them unverified and recommend review.
- Sensitive information exposure: summarize only what is necessary and warn that the input may contain sensitive data.
- User asks for certification: clarify that this skill creates a structured profile, not a certification.
