from __future__ import annotations

import csv
import html
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_EDGE_TYPES = {
    "requires",
    "produces",
    "mitigates",
    "enables",
    "extends",
    "depends_on",
    "informs",
    "competes_with",
}

EDGE_FIELDS = [
    "source_type",
    "source_id",
    "target_type",
    "target_id",
    "edge_type",
    "weight",
    "evidence",
]


@dataclass(frozen=True)
class Concept:
    concept_id: str
    label: str
    category: str
    artifact_reuse: str
    description: str


@dataclass(frozen=True)
class OntologyEdge:
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    edge_type: str
    weight: float
    evidence: str


@dataclass(frozen=True)
class OpportunityBridge:
    name: str
    official_url: str
    bridge_score: float
    related_concepts: list[Concept]
    related_edges: list[OntologyEdge]


@dataclass(frozen=True)
class OntologySnapshot:
    html_path: Path
    edges_path: Path
    opportunities: list[OpportunityBridge]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_concepts(path: Path) -> dict[str, Concept]:
    concepts: dict[str, Concept] = {}
    for row in _read_csv(path):
        concept_id = row.get("concept_id", "").strip()
        if not concept_id:
            continue
        concepts[concept_id] = Concept(
            concept_id=concept_id,
            label=row.get("label", "").strip(),
            category=row.get("category", "").strip(),
            artifact_reuse=row.get("artifact_reuse", "").strip().lower(),
            description=row.get("description", "").strip(),
        )
    return concepts


def load_edges(path: Path) -> list[OntologyEdge]:
    edges: list[OntologyEdge] = []
    for idx, row in enumerate(_read_csv(path), start=2):
        edge_type = row.get("edge_type", "").strip().lower()
        if edge_type not in ALLOWED_EDGE_TYPES:
            raise ValueError(f"Row {idx}: unsupported edge_type {edge_type!r}")
        weight = float(row.get("weight", ""))
        if not 0 <= weight <= 1:
            raise ValueError(f"Row {idx}: weight must be between 0 and 1")
        edges.append(
            OntologyEdge(
                source_type=row.get("source_type", "").strip().lower(),
                source_id=row.get("source_id", "").strip(),
                target_type=row.get("target_type", "").strip().lower(),
                target_id=row.get("target_id", "").strip(),
                edge_type=edge_type,
                weight=weight,
                evidence=row.get("evidence", "").strip(),
            )
        )
    return edges


def related_concept_ids(opportunity_name: str, edges: list[OntologyEdge]) -> list[str]:
    concept_ids: list[str] = []
    for edge in edges:
        if edge.source_type == "opportunity" and edge.source_id == opportunity_name and edge.target_type == "concept":
            concept_ids.append(edge.target_id)
        elif edge.target_type == "opportunity" and edge.target_id == opportunity_name and edge.source_type == "concept":
            concept_ids.append(edge.source_id)
    return concept_ids


def related_opportunity_edges(opportunity_name: str, edges: list[OntologyEdge]) -> list[OntologyEdge]:
    return [
        edge
        for edge in edges
        if (edge.source_type == "opportunity" and edge.source_id == opportunity_name and edge.target_type == "concept")
        or (edge.target_type == "opportunity" and edge.target_id == opportunity_name and edge.source_type == "concept")
    ]


def compute_bridge_score(concepts: list[Concept], edges: list[OntologyEdge]) -> float:
    if not concepts or not edges:
        return 0.0

    categories = {concept.category for concept in concepts if concept.category}
    diversity_factor = min(len(categories) / 3, 1)
    direct_reuse_factor = sum(1 for concept in concepts if concept.artifact_reuse == "direct") / len(concepts)
    relationship_strength = sum(edge.weight for edge in edges) / len(edges)

    score = 100 * (
        0.48 * diversity_factor
        + 0.32 * direct_reuse_factor
        + 0.20 * relationship_strength
    )
    return round(score, 1)


def build_opportunity_bridges(
    opportunities: list[dict[str, str]],
    concepts_by_id: dict[str, Concept],
    edges: list[OntologyEdge],
) -> list[OpportunityBridge]:
    bridges: list[OpportunityBridge] = []
    for opportunity in opportunities:
        name = opportunity.get("name", "").strip()
        concept_ids = related_concept_ids(name, edges)
        related_concepts = [concepts_by_id[cid] for cid in concept_ids if cid in concepts_by_id]
        related_edges = related_opportunity_edges(name, edges)
        bridges.append(
            OpportunityBridge(
                name=name,
                official_url=opportunity.get("official_url", "").strip(),
                bridge_score=compute_bridge_score(related_concepts, related_edges),
                related_concepts=related_concepts,
                related_edges=related_edges,
            )
        )
    return bridges


def write_edges_csv(edges: list[OntologyEdge], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EDGE_FIELDS)
        writer.writeheader()
        for edge in edges:
            writer.writerow(
                {
                    "source_type": edge.source_type,
                    "source_id": edge.source_id,
                    "target_type": edge.target_type,
                    "target_id": edge.target_id,
                    "edge_type": edge.edge_type,
                    "weight": f"{edge.weight:g}",
                    "evidence": edge.evidence,
                }
            )


def _concept_list(concepts: list[Concept]) -> str:
    if not concepts:
        return "<li>No linked concepts yet.</li>"
    return "\n".join(
        f"<li><strong>{html.escape(concept.label)}</strong> "
        f"<span>{html.escape(concept.category)}</span></li>"
        for concept in concepts
    )


def write_snapshot_html(bridges: list[OpportunityBridge], edges: list[OntologyEdge], path: Path) -> None:
    cards = []
    for bridge in sorted(bridges, key=lambda item: item.bridge_score, reverse=True):
        cards.append(
            f"""
      <section class="opportunity">
        <h2>{html.escape(bridge.name)}</h2>
        <p><a href="{html.escape(bridge.official_url)}">{html.escape(bridge.official_url)}</a></p>
        <p><strong>bridge_score:</strong> {bridge.bridge_score}</p>
        <ul>{_concept_list(bridge.related_concepts)}</ul>
      </section>"""
        )
    edge_rows = "\n".join(
        f"<tr><td>{html.escape(edge.source_id)}</td><td>{html.escape(edge.edge_type)}</td>"
        f"<td>{html.escape(edge.target_id)}</td><td>{edge.weight:g}</td></tr>"
        for edge in edges
    )
    path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bounty Ontology Snapshot</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; color: #172026; }}
    main {{ max-width: 960px; margin: 0 auto; }}
    .opportunity {{ border: 1px solid #ccd5df; padding: 1rem; margin: 1rem 0; }}
    h1, h2 {{ margin-bottom: 0.35rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccd5df; padding: 0.5rem; text-align: left; }}
  </style>
</head>
<body>
  <main>
    <h1>Bounty Ontology Snapshot</h1>
    {''.join(cards)}
    <h2>Ontology Edges</h2>
    <table>
      <thead><tr><th>Source</th><th>Type</th><th>Target</th><th>Weight</th></tr></thead>
      <tbody>{edge_rows}</tbody>
    </table>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_ontology_snapshot(
    opportunities_csv: Path,
    concepts_csv: Path,
    edges_csv: Path,
    out_dir: Path,
) -> OntologySnapshot:
    out_dir.mkdir(parents=True, exist_ok=True)
    opportunities = _read_csv(opportunities_csv)
    concepts_by_id = load_concepts(concepts_csv)
    edges = load_edges(edges_csv)
    bridges = build_opportunity_bridges(opportunities, concepts_by_id, edges)

    html_path = out_dir / "ontology_snapshot.html"
    edges_path = out_dir / "ontology_edges.csv"
    write_edges_csv(edges, edges_path)
    write_snapshot_html(bridges, edges, html_path)
    return OntologySnapshot(html_path=html_path, edges_path=edges_path, opportunities=bridges)
