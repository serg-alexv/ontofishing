# Notion Cockpit and Ontology Map Design

## Goal

Design a future Notion cockpit for reviewing bounty opportunities while keeping CSV files as the local source of truth.

This stage does not call the Notion API, require a Notion token, or synchronize any database.

## Source of Truth

Opportunities remain in `data/opportunities_raw.csv` and scored/ranked derivatives such as `data/ranked_opportunities.csv`.

Concepts and ontology edges are local CSV files:

- `data/concepts.example.csv` defines reusable concepts, domains, methods, artifacts, and risks.
- `data/ontology_edges.example.csv` links opportunities and concepts with typed weighted edges.

The Notion cockpit should be a projection of these files, not the canonical store.

## Cockpit Databases

### Opportunities

One row per opportunity from the CSV source.

Suggested properties:

- `Name`
- `Official URL`
- `Decision`
- `Fit Score`
- `Hard Reject`
- `Status Evidence`
- `Eligibility`
- `Deliverable`
- `Bridge Score`
- `Related Concepts`
- `Last CSV Import`

### Concepts

One row per concept from `concepts.example.csv` or the production concepts CSV.

Suggested properties:

- `Concept ID`
- `Label`
- `Category`
- `Artifact Reuse`
- `Description`

### Ontology Edges

One row per edge from the generated `ontology_edges.csv`.

Suggested properties:

- `Source Type`
- `Source ID`
- `Target Type`
- `Target ID`
- `Edge Type`
- `Weight`
- `Evidence`

## Ontology Map Export

The local exporter writes two files:

- `ontology_snapshot.html`: static review surface for bridge scores and linked concepts.
- `ontology_edges.csv`: normalized typed weighted edge list.

The HTML snapshot is intentionally static so it can be opened locally, attached to reports, or copied into a review workflow without credentials.

## Bridge Score

`bridge_score` estimates how much an opportunity connects reusable research work across domains.

It combines:

- Related concept diversity: number of distinct linked concept categories, capped at three categories.
- Direct artifact reuse: share of linked concepts marked `artifact_reuse=direct`.
- Relationship strength: average weight of opportunity-to-concept edges.

This score is advisory only. It does not replace the deterministic opportunity scoring engine.

## Future Sync Boundary

A later Notion sync should:

- Read CSV and generated exports.
- Upsert Notion pages by stable identifiers.
- Preserve local CSV files as the canonical data.
- Never write Notion edits back into scoring inputs without an explicit import command.
- Require an explicit Notion token only in that future sync command.
