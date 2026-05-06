"""Graphify-style graph construction for distilled knowledge."""

from __future__ import annotations

from collections import defaultdict

from .models import KnowledgeClaim, KnowledgeGraph


def build_graph(claims: list[KnowledgeClaim]) -> KnowledgeGraph:
    """Build a typed knowledge graph from deduplicated claims."""

    nodes: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []
    keyword_to_claims: dict[str, list[str]] = defaultdict(list)
    section_to_claims: dict[str, list[str]] = defaultdict(list)

    for claim in claims:
        claim_node_id = f"claim:{claim.id}"
        nodes[claim_node_id] = {
            "id": claim_node_id,
            "type": "claim",
            "label": claim.text[:96],
            "confidence": claim.confidence,
            "source": claim.source_path,
        }
        section_node_id = f"section:{claim.section}"
        nodes.setdefault(section_node_id, {"id": section_node_id, "type": "section", "label": claim.section})
        edges.append({"source": claim_node_id, "target": section_node_id, "type": "from_section"})
        section_to_claims[claim.section].append(claim_node_id)

        for keyword in claim.keywords:
            keyword_node_id = f"keyword:{keyword}"
            nodes.setdefault(keyword_node_id, {"id": keyword_node_id, "type": "keyword", "label": keyword})
            edges.append({"source": claim_node_id, "target": keyword_node_id, "type": "mentions"})
            keyword_to_claims[keyword].append(claim_node_id)

    for keyword, claim_ids in keyword_to_claims.items():
        if len(claim_ids) < 2:
            continue
        for left, right in zip(claim_ids, claim_ids[1:]):
            edges.append({"source": left, "target": right, "type": "related_by_keyword", "keyword": keyword})

    communities = [
        {"id": f"community:{index}", "section": section, "claims": claim_ids}
        for index, (section, claim_ids) in enumerate(sorted(section_to_claims.items()), start=1)
    ]
    return KnowledgeGraph(nodes=list(nodes.values()), edges=edges, communities=communities)
