# Artifact Layout

Every report run must leave a folder with both the final report and the intermediate artifacts.

## Folder rule

Use one root folder per node and period:

`<period>_<node>/`

Inside it, use one subfolder per reporting cycle:

- `2026-01/`
- `2026-02/`
- `2026-Q1/`

## Required files per cycle

Each cycle folder should contain:

1. `00_intake.yaml`
2. `01_bp_anchor_map.yaml`
3. `02_source_inventory.md`
4. `03_evidence_ledger.md`
5. `04_section_cards.md`
6. `05_report.md`

## File purpose

### `00_intake.yaml`

Stores:

- period
- node
- report cycle
- previous baseline path if any
- template and spec paths

### `01_bp_anchor_map.yaml`

Stores:

- goals
- key results
- measure standards
- owners and assignees

### `02_source_inventory.md`

Stores:

- adopted report counts and breakdown
- all adopted evidence sources
- source priority
- whether each source is owner-authored or auxiliary

### `03_evidence_ledger.md`

Stores:

- month evidence lines
- source links
- confidence
- traffic-light support notes

### `04_section_cards.md`

Stores:

- section-by-section drafting cards
- chosen evidence
- traffic-light judgments
- open gaps

### `05_report.md`

Stores the final monthly or quarterly report draft.

## Source linking rule

Do not create one local snapshot file per adopted report by default.

The final report and the intermediate markdown artifacts should point directly to the BP report itself, preferably with:

- `[工作汇报标题](reportId=<工作汇报id>&linkType=report)`

If the current API response does not expose `reportId`, keep the minimal source metadata inline:

- title
- author
- task mapping
- evidence priority
- `report_link_status: missing_report_id`

## Minimum source metadata

Each adopted source entry should contain:

- source id, such as `R001`
- report title
- report id when available
- report link markdown when available
- report author
- linked BP task
- source priority: primary / secondary / auxiliary / summary_only
- report type
- concrete progress extraction
- attachment metadata if available

The file header should also contain:

- total raw-hit work-report count
- total adopted work-report count
- adopted owner-authored report count
- adopted other-manual report count
- adopted AI report count
- a short source-coverage note
- a short batch-collapse note when notification-style reports were merged

Optional:

- a short note that explains why the source was adopted
- exported attachment files only when the upstream API exposes downloadable attachment links and the user wants local retention
