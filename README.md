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
