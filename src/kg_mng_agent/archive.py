"""BMAD-style durable knowledge archive writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import DedupDecision, KnowledgeClaim, KnowledgeGraph, SourceDocument
from .specs import render_spec_markdown


def archive_run(
    document: SourceDocument,
    claims: list[KnowledgeClaim],
    deduped_claims: list[KnowledgeClaim],
    decisions: list[DedupDecision],
    graph: KnowledgeGraph,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Write manifest, Markdown report, graph JSON, and active spec files."""

    archive_dir = output_dir.expanduser().resolve() / _safe_stem(document.path) / document.sha256[:12]
    archive_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = archive_dir / "manifest.json"
    graph_path = archive_dir / "graph.json"
    report_path = archive_dir / "distilled.md"
    spec_path = archive_dir / "spec.md"

    manifest = {
        "source": str(document.path),
        "media_type": document.media_type,
        "sha256": document.sha256,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "architecture": ["data", "processing", "application"],
        "framework_lineage": ["BMAD structured archive", "Graphify knowledge graph", "OpenSpec requirements", "SpecKit lifecycle validation"],
        "claim_count": len(claims),
        "deduped_claim_count": len(deduped_claims),
        "duplicate_count": len(decisions),
        "artifacts": {"report": report_path.name, "graph": graph_path.name, "spec": spec_path.name},
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    graph_path.write_text(json.dumps(_graph_to_dict(graph), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(document, deduped_claims, decisions, graph), encoding="utf-8")
    spec_path.write_text(render_spec_markdown(), encoding="utf-8")
    return manifest_path, report_path, graph_path


def _render_report(document: SourceDocument, claims: list[KnowledgeClaim], decisions: list[DedupDecision], graph: KnowledgeGraph) -> str:
    lines = [
        f"# Distilled Knowledge: {document.path.name}",
        "",
        "## Three-layer Architecture Trace",
        "",
        f"- Data layer: `{document.path}` ({document.media_type}, sha256 `{document.sha256}`)",
        "- Processing layer: source-grounded distillation → graph consolidation → duplicate review",
        "- Application layer: Markdown report, JSON graph, manifest, and spec contract",
        "",
        "## Knowledge Claims",
        "",
    ]
    for claim in claims:
        lines.extend(
            [
                f"### {claim.id}: {claim.section}",
                "",
                f"- Claim: {claim.text}",
                f"- Keywords: {', '.join(claim.keywords) if claim.keywords else 'n/a'}",
                f"- Confidence: {claim.confidence:.2f}",
                "",
            ]
        )
    lines.extend(["## Duplicate Review", ""])
    if decisions:
        for decision in decisions:
            lines.append(f"- Removed `{decision.duplicate_id}` in favor of `{decision.kept_id}` ({decision.reason}, similarity {decision.similarity:.3f}).")
    else:
        lines.append("- No duplicate claims were removed.")
    lines.extend(
        [
            "",
            "## Graph Summary",
            "",
            f"- Nodes: {len(graph.nodes)}",
            f"- Edges: {len(graph.edges)}",
            f"- Communities: {len(graph.communities)}",
            "",
        ]
    )
    return "\n".join(lines)


def _graph_to_dict(graph: KnowledgeGraph) -> dict[str, object]:
    return {"nodes": graph.nodes, "edges": graph.edges, "communities": graph.communities}


def _safe_stem(path: Path) -> str:
    return "".join(character if character.isalnum() or character in "-_" else "-" for character in path.stem).strip("-") or "document"
