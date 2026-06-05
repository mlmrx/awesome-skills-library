# Security Policy

Awesome Skills Library contains agent-facing instructions and metadata. Security concerns may involve unsafe workflows, misleading trust claims, dangerous permissions, prompt-injection exposure, data handling risks, or compatibility claims that could cause misuse.

## Reporting a concern

Open a security concern issue if public discussion is safe. If the concern includes sensitive exploit details, private data, or active abuse, contact the maintainers privately before publishing details.

Include:

- affected skill or file path;
- risk summary;
- reproduction steps or example input when safe;
- expected safer behavior;
- suggested mitigation, if known.

## Maintainer response

Maintainers should triage security reports based on severity, exploitability, and likely impact. Possible responses include updating safety boundaries, changing metadata, removing a skill, or adding validation checks.

## Scope

In scope:

- unsafe skill instructions;
- inaccurate permission or compatibility metadata;
- missing safety boundaries for sensitive tasks;
- test gaps that permit dangerous behavior;
- scripts that corrupt repository data.

Out of scope:

- general AI model behavior unrelated to this repository;
- vulnerabilities in third-party agent runtimes;
- requests for production security guarantees from sample skills.
