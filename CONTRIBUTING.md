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
