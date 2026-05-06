from __future__ import annotations

import json
from pathlib import Path

from kg_mng_agent.agent import KnowledgeAgent
from kg_mng_agent.dedup import deduplicate_claims
from kg_mng_agent.models import KnowledgeClaim


def test_agent_archives_distilled_graph_and_spec(tmp_path: Path) -> None:
    source = tmp_path / "strategy.md"
    source.write_text(
        "# Knowledge Architecture\n\n"
        "The system SHALL ingest documents and create source grounded knowledge claims for every important requirement.\n"
        "The system SHALL ingest documents and create source grounded knowledge claims for every important requirement.\n"
        "Graph consolidation links claims to keywords and sections so downstream agents can query relationships.\n"
        "# Archive\n\n"
        "Lifecycle archives keep a manifest, distilled report, graph output, and specification for review.\n",
        encoding="utf-8",
    )

    run = KnowledgeAgent(output_dir=tmp_path / "kb", dedup_threshold=0.7).run(source)

    assert run.report_path.exists()
    assert run.graph_path.exists()
    assert run.manifest_path.exists()
    assert (run.archive_dir / "spec.md").exists()
    assert len(run.deduped_claims) < len(run.claims)
    graph = json.loads(run.graph_path.read_text(encoding="utf-8"))
    assert any(node["type"] == "claim" for node in graph["nodes"])
    assert any(edge["type"] == "mentions" for edge in graph["edges"])
    report = run.report_path.read_text(encoding="utf-8")
    assert "Three-layer Architecture Trace" in report
    assert "Duplicate Review" in report


def test_deduplicate_claims_records_near_duplicate_decision() -> None:
    claims = [
        KnowledgeClaim("K0001", "Graph consolidation links claims to sections and keywords.", "doc.md", "Graph", ("graph", "claims"), 0.9),
        KnowledgeClaim("K0002", "Graph consolidation links claims to keywords and sections.", "doc.md", "Graph", ("graph", "claims"), 0.8),
    ]

    kept, decisions = deduplicate_claims(claims, threshold=0.6)

    assert [claim.id for claim in kept] == ["K0001"]
    assert decisions[0].kept_id == "K0001"
    assert decisions[0].duplicate_id == "K0002"
