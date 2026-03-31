# Changelog

## 1.4.0
- Tightened the output contract to exactly two user-facing artifacts:
  - one pure publish bundle zip
  - one separate plain-text review file
- Removed support-file concepts that implied extra user-facing artifact classes
- Clarified that review, inference, and build commentary must stay out of the publish bundle
- Clarified that the packager defaults to the full release-bundle standard, not the minimal valid skill standard
- Added a deliverable-separation review category to the checklist
- Added a visibility rule requiring both final artifacts to be surfaced directly to the user
- Preserved the intentional short runtime name vs fuller skill key identity split
- Preserved slash-only explicit invocation via `disable-model-invocation: true`

## 1.3.0
- Added explicit mapping between support files and their output roles
- Added named operating modes for package-from-scratch, repair-existing-skill, audit-only, republish/update, and rename/rebrand
- Connected the two-pass workflow to each named mode
- Added skill type awareness for instruction-only, code, API, env-var, binary, and mixed packages
- Added runtime and security declaration review guidance
- Added `PUBLISH-HANDOFF.txt` as a standard artifact
- Defined severity markers explicitly
- Documented the intentional split between short runtime name and fuller skill key identity
- Preserved low-friction, inference-first packaging stance
- Preserved slash-only explicit invocation via `disable-model-invocation: true`

## 1.2.0
- Expanded the packager beyond text-only skill packaging into broader package-scope analysis
- Added runtime declarations review for skills with external requirements
- Added deeper security-scope analysis for non-text skill packages
- Added file-type awareness for scripts, APIs, env vars, binaries, and mixed package classes
- Improved search and discoverability coverage for broader skill package types
- Treated the `disable-model-invocation` choice as a runtime validation question rather than a settled desk-only decision

## 1.1.0
- Polished the skill around low-friction, inference-first packaging behavior
- Added explicit no-question-loop operating stance
- Added stronger delivery contract for package + review summary
- Clarified second-pass workflow after user revisions
- Strengthened emphasis on clear assumptions, fixes, and review flags
- Preserved two-pass audit and packaging design

## 1.0.0
- Initial release
- Added two-pass audit and package generation workflow
- Added plain-text review record requirement
- Added frontmatter normalization guidance
- Added naming alignment rules for display name, slug, skill key, and folder
- Added ClawHub/OpenClaw package review checklist
- Added highlighted review markers for inferred or risky fields