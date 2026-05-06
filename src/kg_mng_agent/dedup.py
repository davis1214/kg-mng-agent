"""Knowledge deduplication inspired by graph and spec-review workflows."""

from __future__ import annotations

import re

from .models import DedupDecision, KnowledgeClaim

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}")


def deduplicate_claims(claims: list[KnowledgeClaim], threshold: float = 0.82) -> tuple[list[KnowledgeClaim], list[DedupDecision]]:
    """Remove exact and near-duplicate claims while preserving an audit trail."""

    kept: list[KnowledgeClaim] = []
    decisions: list[DedupDecision] = []
    for claim in claims:
        duplicate_of: KnowledgeClaim | None = None
        duplicate_similarity = 0.0
        reason = ""
        normalized = _normalize_text(claim.text)
        for existing in kept:
            exact = normalized == _normalize_text(existing.text)
            similarity = 1.0 if exact else _jaccard(_tokens(claim.text), _tokens(existing.text))
            if exact or similarity >= threshold:
                duplicate_of = existing
                duplicate_similarity = similarity
                reason = "exact normalized match" if exact else "near-duplicate token overlap"
                break
        if duplicate_of is None:
            kept.append(claim)
            continue
        decisions.append(
            DedupDecision(
                kept_id=duplicate_of.id,
                duplicate_id=claim.id,
                reason=reason,
                similarity=round(duplicate_similarity, 3),
            )
        )
    return kept, decisions


def _normalize_text(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
