---
name: improve-skill-with-best-practices
description: "Improves existing skills or guides creation of new skills by applying official skill authoring best practices. Covers conciseness optimization, progressive disclosure, freedom calibration, workflow design, script quality, and description effectiveness. Use when creating a new skill with best practices, reviewing or optimizing an existing skill, or when the user mentions skill improvement, skill creation, or skill quality."
---

# Improve Skill With Best Practices

Create high-quality new skills or systematically improve existing ones by applying official skill authoring best practices.

## Prerequisite

Before starting any work, load these references:
- `references/best-practices.md` — full catalog of authoring principles
- `references/skill-anatomy.md` — skill structure, resource types, progressive disclosure
- `references/fix-priority.md` — quality principles and prioritized fix categories

Assume all skill content — whether newly drafted or pre-existing — has NOT been designed according to best practices.

## Mode Selection

- **Create Mode** — Build a new skill from scratch
- **Improve Mode** — Review and optimize an existing skill

---

## Create Mode

1. **Clarify intent** — Gather concrete usage examples: what triggers the skill, what it produces, how it would be used
2. **Plan resources** — Map examples to resource types (see `references/skill-anatomy.md`)
3. **Initialize** — `python3 scripts/init_skill.py <skill-name> --path <parent-dir>`
4. **Choose structure pattern** — Workflow / Task / Reference / Capabilities (see `references/skill-anatomy.md`)
5. **Draft SKILL.md** — Cross-check every section against `references/best-practices.md` and `references/fix-priority.md`
6. **Implement resources** — Create scripts, references, assets. Delete unused scaffolding files. Apply best practices to all content
7. **Analyze** — `python3 scripts/analyze_skill.py <path>`
8. **Fix** — Address findings by priority (see `references/fix-priority.md`)
9. **Validate & package**:
   ```
   python3 scripts/quick_validate.py <path>
   python3 scripts/package_skill.py <path> [output-dir]
   ```
10. **Iterate** — Re-analyze, test with real scenarios, refine

---

## Improve Mode

1. **Read the skill** — Load target SKILL.md and all bundled resources
2. **Analyze** — `python3 scripts/analyze_skill.py <path>`
3. **Manual audit** — Review all content against `references/best-practices.md` and `references/fix-priority.md`. Automated analysis catches structural issues; manual review catches tone, conciseness, freedom calibration, and disclosure problems
4. **Consolidate** — Merge automated + manual findings into a single prioritized list
5. **Fix** — Apply improvements by priority (Critical → Recommended → Optional)
6. **Re-analyze** — `python3 scripts/analyze_skill.py <path>`
7. **Validate** — `python3 scripts/quick_validate.py <path>`
8. **Summary** — Present before/after comparison

---

## Bundled Scripts

| Script | Purpose |
|---|---|
| `init_skill.py` | Scaffold new skill directory |
| `analyze_skill.py` | Automated best-practices analysis |
| `quick_validate.py` | Fast frontmatter and structure validation |
| `package_skill.py` | Package skill into distributable zip |

## Finalize

Before finalizing any skill, verify against `references/checklist.md`. Copy the checklist and mark items during review.
