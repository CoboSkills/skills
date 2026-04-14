---
name: llm-wiki
description: Build, maintain, query, archive, and audit a Markdown / Obsidian knowledge Wiki continuously maintained by an LLM. Use this skill to initialize a personal knowledge base; import raw materials grouped by source under source/ into wiki/; organize articles, papers, book notes, interviews, and meeting notes; maintain source pages, entity pages, concept pages, synthesis pages, comparison pages, and query archive pages; update index.md and log.md; answer questions based on the Wiki and archive answers with long-term value; check broken links, orphan pages, duplicate concepts, outdated conclusions, unlabeled contradictions, encoding corruption, and organizational disorder.
---

# LLM Wiki

## Goal

Maintain a Markdown / Obsidian Wiki that is accumulative, linkable, and evolvable. Whenever importing material or answering a question, do not merely generate a summary. Instead, compile new knowledge into existing pages: update entities, concepts, synthesized judgments, comparisons, and query archives so the Wiki becomes more valuable through continued use.

## Default Three-Layer Structure

```text
source/          # Raw material layer: factual sources, read-only by default
wiki/            # Knowledge compilation layer: structured Wiki maintained by the LLM
schema/SKILL.md  # Convention layer: this skill / schema
```

### source/

- Raw materials are read-only by default. Do not rewrite their body text.
- Preserve original titles, authors, URLs, dates, clipping metadata, image references, and similar source information.
- If original materials need to be renamed or supplemented with metadata, ask the user for confirmation first.

### wiki/

Use English for the default directory structure:

```text
wiki/
  index.md      # Main index
  log.md        # Operation log
  README.md     # Wiki documentation
  sources/
  entities/
  concepts/
  syntheses/
  comparisons/
  queries/
```

Conventions:

- Except for agreed convention files such as `index.md`, `log.md`, `README.md`, and `schema/SKILL.md`, use readable English names for directories and files whenever possible.
- Terminological proper nouns may remain in their original language or use mixed naming when appropriate, for example `AI Agent.md`, `OpenClaw.md`, `Claude Code.md`, or `Harness Engineering.md`.
- Do not create redundant parallel directories such as both `concept/` and `concepts/`, or both `entity/` and `entities/`. If historical empty duplicates are found, clean them up. If they contain content, migrate that content into the canonical directory and update links.
- File names should be readable, clickable, and maintainable over the long term. Avoid machine-style prefixes such as `source-*`, `concept-*`, or `synthesis-*`.

## Page Types

### Source Pages: `wiki/sources/`

Use source pages to summarize and locate a single source. A source page should include:

- Source information: original file, URL, author, and date.
- A one-sentence summary.
- The question this source helps answer.
- Key structure / section clues.
- Knowledge points worth preserving.
- Related concept / entity / synthesis pages.
- Follow-up close-reading tasks.

### Entity Pages: `wiki/entities/`

Use entity pages for people, organizations, products, projects, tools, and similar objects. Entity pages hold facts and background; they should not carry excessively long arguments.

- Create entity pages only for knowledge objects: people, organizations, products, projects, tools, and similar items should enter the entity layer only when they themselves are analysis objects or when they carry reusable facts. Do not create an entity page merely because someone is the author of a source. Do not maintain article-author lists on entity pages. Keep author information in the source page's source information or in `source/` metadata.

### Concept Pages: `wiki/concepts/`

Use concept pages for methods, patterns, theories, problem framings, frameworks, and similar ideas. Prefer reusing and updating existing concept pages to avoid synonym duplication.

### Synthesis Pages: `wiki/syntheses/`

Use synthesis pages for cross-source judgments, frameworks, thematic overviews, case matrices, architecture analyses, and similar compiled knowledge.

### Comparison Pages: `wiki/comparisons/`

Use comparison pages to compare concepts, products, paradigms, and solutions, for example `Reasoner vs Agent.md`.

### Query Pages: `wiki/queries/`

Archive question-and-answer outputs with long-term value as reusable pages. A query page should answer a clear question and link back to related source, concept, and synthesis pages.

## Core Workflows

### Initialize the Wiki

1. Scan the directories, file types, and source groupings under `source/`.
2. Create or update `wiki/index.md`, `wiki/log.md`, and `wiki/README.md`.
3. Create source pages for the first batch of materials.
4. Extract entity, concept, synthesis, and comparison pages.
5. Update the index and log.
6. Check broken links, encoding corruption, duplicate directories, and empty directories.

### Import Materials

1. Read `wiki/index.md` first to locate existing related pages.
2. Read the new source and extract its summary, key structure, entities, concepts, and reusable judgments.
3. Create or update the source page.
4. Update existing entity pages, concept pages, and synthesis pages. Prefer updating existing pages; do not lightly create duplicate concepts.
5. Mark relationships: supports, supplements, revises, contradicts, or needs verification.
6. Update `wiki/index.md` and `wiki/log.md`.
7. Run broken-link and encoding-corruption checks.

### Answer Questions Based on the Wiki

1. Read `wiki/index.md` first.
2. Then read relevant pages. Do not scan the entire Wiki by default.
3. Cite Wiki page links in the answer.
4. If the answer has long-term value, archive it under `wiki/queries/` or update a synthesis page.
5. Update `wiki/log.md`.

## `index.md` Specification

`wiki/index.md` is the navigation entry point. Recommended structure:

```markdown
# Knowledge Wiki Index

## Quick Links

## Sources

## Entities

## Concepts

## Syntheses

## Comparisons

## Queries
```

Each record should preferably include:

```markdown
- [[Knowledge/wiki/concepts/Context Engineering]] -- one-sentence description; status: evolving.
```

## `log.md` Specification

`wiki/log.md` is a date-based timeline for phase-level changes, not an overly granular operation ledger. Update principles:

- **Merge by date**: imports, refactors, queries, and maintenance performed on the same day should be merged under `## YYYY-MM-DD | Topic Overview` whenever possible, using `###` to group by topic.
- **Record phase-level results**: preserve key sources, key newly created or updated pages, core conclusions, and important maintenance decisions. Do not append a separate entry for every small operation.
- **Create separate detail pages when needed**: place bulk mappings, long audit checklists, image migration tables, complex experiment logs, and similar details under `wiki/maintenance/`, `wiki/queries/`, or the relevant synthesis page. `log.md` should only link to a summary.
- **Rewrite the same-day section when updating multiple times in one day**: prefer editing and merging the existing section for the day instead of appending fragmented entries.
- **Preserve follow-up direction**: a short "Current To-Dos / Follow-Up Directions" list may be maintained at the end, but keep it concise.

Recommended format:

```markdown
## YYYY-MM-DD | Topic Overview

### Topic One

- Import/update scope: ...
- Created/updated: [[Knowledge/wiki/...]], [[Knowledge/wiki/...]]
- Key conclusion: ...

### Topic Two

- ...

## Current To-Dos / Follow-Up Directions

- [ ] ...
```

Common topics:

- Initialization and structural adjustment.
- Topic-based source import.
- Concept / synthesis page deepening.
- Query archiving.
- Audit and maintenance.
- Schema / skill rule updates.

## Frontmatter Recommendations

Source page:

```yaml
---
type: source
tags: [source-summary]
source_file: "[[Knowledge/source/...]]"
source_name:
author:
url:
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: initialized
---
```

Entity page:

```yaml
---
type: entity
tags: [entity]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: evolving
---
```

Concept page:

```yaml
---
type: concept
tags: [concept]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: evolving
---
```

Synthesis page:

```yaml
---
type: synthesis
tags: [synthesis]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: evolving
---
```

Comparison page:

```yaml
---
type: comparison
tags: [comparison]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: evolving
---
```

Query page:

```yaml
---
type: query
tags: [query]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: archived
---
```

## Link Rules

- Use Obsidian Wiki links: `[[Knowledge/wiki/concepts/Context Engineering]]`.
- When linking to vault files, use paths relative to the vault root. Do not use absolute paths.
- After renaming files, batch-update all `[[...]]` links.
- When responding to the user, prefer clickable Wiki links whenever possible.

## Encoding Safety Rules

English content should be written as UTF-8. In Windows / PowerShell environments, writing non-ASCII text directly with PowerShell here-strings, `Add-Content`, or `Set-Content` may produce replacement characters or other encoding corruption.

Prefer:

- Use `apply_patch` to modify Markdown;
- Or create a `.py` script and write text with `Path.write_text(..., encoding="utf-8")`;
- Or verify file content with Python `read_text(..., encoding="utf-8")`.

Avoid:

- Writing large non-ASCII blocks directly inside PowerShell command strings;
- Judging whether a file is corrupted based only on terminal display output.

After every batch write, check for:

- Repeated question marks;
- Unicode replacement characters;
- Typical mojibake markers;
- Broken links.

## Images and Attachments

- Do not batch-download external images in `source/` by default, unless the user requests it or the image is critical for long-term understanding.
- If images need to be localized, download them to the vault attachment location and convert the Markdown image syntax to an Obsidian image embed: `![[image.png]]`.
- The raw material layer is read-only by default. Confirm before localizing images or rewriting original materials.

## Safety Principles

- Do not overwrite the user's original materials.
- Do not delete non-empty directories unless you have confirmed that their contents have been migrated or the user explicitly requested deletion.
- Before bulk moves or renames, create a mapping. After execution, check broken links.
- Explicit user preferences override this schema, for example directory naming, whether reports should be kept, or whether `README.md` should keep its English name.
