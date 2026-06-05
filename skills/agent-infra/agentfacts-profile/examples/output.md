# AgentFacts Profile: DataDesk Assistant

## Identity

- Name: DataDesk Assistant
- Type: AI agent for data-analysis assistance
- Profile status: based on supplied information only; not independently verified

## Owner / Operator

- Publisher: Example Analytics Lab
- Operator contact: unknown
- Maintainer contact: unknown

## Purpose

DataDesk Assistant helps analysts summarize CSV files, draft SQL queries, and prepare short data quality notes.

## Capabilities

- Summarizes uploaded tabular data.
- Drafts SQL queries from natural-language requests and optional schema notes.
- Produces Markdown summaries and data-quality checklists.
- Does not execute SQL directly based on the supplied information.

## Input Contract

- Accepted inputs: CSV-like tabular data, natural-language analysis requests, and optional database schema notes.
- Required context: the user's analysis goal and any schema details needed for SQL drafting.
- Sensitive input concern: users may paste customer data into prompts.
- Rejected or unsupported inputs: unknown.

## Output Contract

- Output types: Markdown summaries, draft SQL, and data-quality checklists.
- Execution behavior: generated SQL must be reviewed and run by a human analyst in a separate environment.
- Known limitations: no evidence was supplied for privacy, security, or reliability guarantees.

## Trust Claims

- "Safe for enterprise use": unverified; no audit report or evaluation evidence supplied.
- "Does not leak data": unverified; no privacy policy, technical controls, or independent assessment supplied.
- "Does not execute SQL directly": self-asserted by supplied information.

## Verification Metadata

- Evidence sources: user-provided project description.
- Independent verification performed: no.
- Review date: unknown.
- Evaluator: unknown.
- Confidence: medium for stated workflow details; low for security and privacy claims.

## Risk Notes

- Privacy risk: users may submit customer data.
- Misrepresentation risk: enterprise safety and data-leakage claims are unsupported.
- Operational risk: draft SQL may be incorrect and should be reviewed before execution.
- Reliance risk: users may mistake a structured profile for certification.

## Human Review Recommendation

Human review is recommended before integrating this agent into a workflow, especially for privacy handling, security claims, SQL correctness, and operator accountability.

## Verification Gaps

- Operator or support contact.
- Privacy policy and data retention details.
- Security controls and audit evidence.
- Evaluation results for SQL quality and data-summary reliability.
- Clear policy for handling customer data.
