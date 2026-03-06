---
name: mindgraph
version: 5.0.0
description: "Structured knowledge graph with 18 cognitive tools for agent memory and reasoning"
author: shuruheel
---

# MindGraph Skill

MindGraph is a **structured knowledge graph index** for sub-agents, cross-file constraint lookups, and semantic search. Files (MEMORY.md, daily notes) are canonical — MindGraph provides structured relationships and search on top of them.

---

## Design Conventions

1.  **Agent Identity:** Always pass `agent_id: 'jaadu'` (or `claude` if in that context) to ensure accurate `changed_by` provenance.
2.  **Atomic Bundling:** Use bundle endpoints (`/epistemic/argument`, `/action/procedure`, `/agent/plan`) to create related nodes and edges in a single transaction.
3.  **Narration:** Narrate before writing to `/memory/config` or `/agent/governance` as these modify behavioral rules.
4.  **Session Framing:** Call `POST /memory/session (action: open)` at the start of each conversation and use the `session_uid` for trace entries and distillation.

---

## Cognitive Layer Endpoints (The 18 Tools)

### Reality Layer (Raw Input)
- **POST /reality/ingest:** Capture `source` (web/paper/book), `snippet` (auto-links to source), or `observation`.
- **POST /reality/entity:** `create` (dedup-safe via `find_or_create_entity` — checks alias + case-insensitive match before creating, returns `{node, created: bool}`), `alias`, `resolve`, `fuzzy_resolve`, or `merge`.

### Epistemic Layer (Reasoning)
- **POST /epistemic/argument:** Atomic Toulmin bundle. Creates `Claim` + `Evidence` + `Warrant` + `Argument` nodes and wires `Supports`, `HasWarrant`, `HasPremise`, and `HasConclusion` edges.
- **POST /epistemic/inquiry:** Record `hypothesis`, `anomaly`, `assumption`, `question`, or `open_question`. Handles `AnomalousTo`, `Tests`, and `Addresses` edges.
- **POST /epistemic/structure:** Crystallize `concept`, `pattern`, `mechanism`, `model`, `analogy`, `theorem`, or `equation`. Handles `AnalogousTo` and `TransfersTo` edges.

### Intent Layer (Commitments)
- **POST /intent/commitment:** Declare `goal`, `project`, or `milestone`. Propose before creating Goals/Projects.
- **POST /intent/deliberation:** Manage `open_decision`, `add_option`, `add_constraint`, or `resolve` (creates `DecidedOn` edge).

### Action Layer (Workflows)
- **POST /action/procedure:** Design `create_flow`, `add_step`, `add_affordance`, or `add_control` (wires `ComposedOf`, `StepUses`, `Controls`).
- **POST /action/risk:** `assess` a node (severity/likelihood) or `get_assessments`.

### Memory Layer (Persistence)
- **POST /memory/session:** `open`, `trace` (real-time recording), or `close` (links to summary).
- **POST /memory/distill:** synthesis of a session into a durable `Summary` node.
- **POST /memory/config:** `set_preference`, `set_policy`, `get_preferences`, or `get_policies`.

### Agent Layer (Control)
- **POST /agent/plan:** `create_task`, `create_plan`, `add_step`, or `update_status`.
- **POST /agent/governance:** `create_policy`, `set_budget`, `request_approval`, or `resolve_approval`.
- **POST /agent/execution:** `start`, `complete`, `fail`, or `register_agent`.

### Memory Layer — Journal (Phase 0.5.6)
- **Journal nodes** via `POST /node` with `node_type: "Journal"`. Props: `content`, `session_uid`, `journal_type` (note/investigation/debug/reasoning), `tags`.
- Use `Follows` edges between Journal nodes for temporal sequencing (debugging arcs, reasoning chains).

### Connective Tissue
- **POST /retrieve:** Unified search modes: `text`, `semantic`, `hybrid` (RRF fusion of FTS + vector, k=60 — falls back to FTS-only if no embeddings), `active_goals`, `open_questions`, `weak_claims`, `pending_approvals`, `layer`, `recent`.
- **POST /traverse:** Navigation modes: `chain`, `neighborhood`, `path`, `subgraph`.
- **POST /evolve:** Mutation: `update` (propsPatch now validated — returns 422 with `unknown_props_fields` for invalid fields), `tombstone` (with cascade), `restore`, `decay`, `history`, `snapshot`.

### Full-Content FTS (Phase 0.5.2)
FTS indexes **all user-authored text** across 35+ string fields and 43+ Vec<String> fields — not just label and summary. Auto-indexed on insert/update. Run `node reindex-search.js` after upgrading to reindex existing nodes.

---

## Client API (mindgraph-client.js)

The client library wraps these cognitive endpoints. See `mindgraph-client.js` for full method signatures.

```javascript
const mg = require('./mindgraph-client.js');
// Example: Atomic Toulmin Bundle
await mg.addArgument({
  claim: { label: "Succession crisis likely", content: "Khamenei's death creates a power vacuum" },
  evidence: [{ label: "IRGC mobilization", description: "Reports of IRGC units entering Tehran" }],
  warrant: { label: "Historical precedent", explanation: "Regime transitions in Iran are often IRGC-led" }
});

// Phase 0.5 additions:
await mg.addJournal("Debug: propsPatch issue", "Full investigation notes...", { journalType: 'investigation', tags: ['bug'] });
await mg.hybridSearch("propsPatch validation", { limit: 5 });  // Server-side RRF
await mg.findOrCreateEntity("Aaron Goh", "Person");  // Dedup-safe
await mg.addFollowsEdge(journalUid1, journalUid2);   // Temporal chain
```
