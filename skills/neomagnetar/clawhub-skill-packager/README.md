# clawhub-skill-packager

A ClawHub / OpenClaw skill for reviewing, repairing, packaging, and self-auditing other ClawHub/OpenClaw skills.

## Display Name
ClawHub Skill Packager

## Goal
Take any combination of:
- a user description
- existing skill files
- partial metadata
- draft naming
- invocation ideas
- packaging notes

and turn it into exactly two user-facing outputs:
1. a publish-ready skill package zip
2. a separate plain-text review file

## Core philosophy
This skill is built for low-friction handoff.

The user should be able to hand over draft material and receive:
- a completed release-style package zip
- a separate review file
- a clear summary of what was inferred, fixed, changed, or flagged

The skill should minimize question loops and favor best-effort packaging plus clear review notes.

## Runtime identity note
This package intentionally uses:
- `clawhub-pack` as the short runtime / slash identity
- `clawhub-skill-packager` as the fuller slug / skill key identity

## What it does

This skill:
- audits what is already present
- identifies what is missing
- fills gaps using safe defaults when needed
- repairs naming and frontmatter issues
- aligns slug, skill key, and package naming
- builds the final folder
- performs a second-pass self-review
- produces one pure publish bundle zip
- produces one separate plain-text review file

## Release-style boundary

The publish zip should contain only files that directly belong to the skill as a release artifact.

The review file should remain outside the publish zip and should contain:
- inputs received
- missing information
- assumptions
- changes made
- review flags
- publish-readiness
- handoff details

## Included support files in this skill package

These are part of the packager skill itself:
- `REVIEW-CHECKLIST.txt`
- `REVIEW-RECORD-TEMPLATE.txt`

## Publish fields
- Slug: `clawhub-skill-packager`
- Internal skill name / slash command: `clawhub-pack`
- Skill key: `clawhub-skill-packager`
- Version: `1.4.0`
- Tags: `latest, clawhub, openclaw, packaging, review, audit, skills`
