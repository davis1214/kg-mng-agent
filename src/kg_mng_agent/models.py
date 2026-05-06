"""Typed data structures for the knowledge-management pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceDocument:
    """Normalized raw document from the data layer."""

    path: Path
    media_type: str
    text: str
    sha256: str


@dataclass(frozen=True)
class KnowledgeClaim:
    """A distilled, source-grounded atomic knowledge claim."""

    id: str
    text: str
    source_path: str
    section: str
    keywords: tuple[str, ...]
    confidence: float


@dataclass(frozen=True)
class DedupDecision:
    """Records how duplicate or near-duplicate claims were handled."""

    kept_id: str
    duplicate_id: str
    reason: str
    similarity: float


@dataclass(frozen=True)
class KnowledgeGraph:
    """Graphify-style graph output represented without runtime service dependencies."""

    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    communities: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeRun:
    """All outputs produced by one CLI execution."""

    source: SourceDocument
    claims: list[KnowledgeClaim]
    deduped_claims: list[KnowledgeClaim]
    dedup_decisions: list[DedupDecision]
    graph: KnowledgeGraph
    archive_dir: Path
    report_path: Path
    graph_path: Path
    manifest_path: Path
