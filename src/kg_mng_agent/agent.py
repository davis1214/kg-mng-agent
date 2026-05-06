"""Unified knowledge-management subagent orchestration."""

from __future__ import annotations

from pathlib import Path

from .archive import archive_run
from .dedup import deduplicate_claims
from .distill import distill_claims
from .extractors import read_document
from .graph import build_graph
from .models import KnowledgeRun


class KnowledgeAgent:
    """Three-layer agent: data input, processing, and knowledge-service outputs."""

    def __init__(self, output_dir: Path | str = ".kgmng/knowledge", max_claims: int = 40, dedup_threshold: float = 0.82) -> None:
        self.output_dir = Path(output_dir)
        self.max_claims = max_claims
        self.dedup_threshold = dedup_threshold

    def run(self, file_path: Path | str) -> KnowledgeRun:
        """Distill, deduplicate, graph, and archive a supported document."""

        source = read_document(Path(file_path))
        claims = distill_claims(source, max_claims=self.max_claims)
        deduped_claims, decisions = deduplicate_claims(claims, threshold=self.dedup_threshold)
        graph = build_graph(deduped_claims)
        manifest_path, report_path, graph_path = archive_run(
            source,
            claims,
            deduped_claims,
            decisions,
            graph,
            self.output_dir,
        )
        return KnowledgeRun(
            source=source,
            claims=claims,
            deduped_claims=deduped_claims,
            dedup_decisions=decisions,
            graph=graph,
            archive_dir=manifest_path.parent,
            report_path=report_path,
            graph_path=graph_path,
            manifest_path=manifest_path,
        )
