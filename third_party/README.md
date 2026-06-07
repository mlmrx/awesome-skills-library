# Third-party skills

`third_party/skills/` contains third-party skills copied into Awesome Skills Library only after a license review determines that redistribution is allowed.

Rules for this area:

- Every copied skill must include attribution metadata (`ATTRIBUTION.md` and `source.yaml`).
- Skills without compatible redistribution licenses are not copied.
- Unknown-license skills are cataloged only in `catalog/` and are not copied here.
- Source-available skills are cataloged only unless their terms explicitly allow redistribution.
- Curated original Awesome Skills Library skills stay in `skills/`.
- Imported third-party skills stay in `third_party/skills/`.

Subdirectories:

- `third_party/skills/anthropics/` — redistributable skills copied from Anthropic's official skills repository.
- `third_party/skills/community/` — redistributable community skills copied from public GitHub repositories.

Do not execute imported scripts during import. The import pipeline copies files and records provenance only.
