"""Knowledge distillation primitives."""

from __future__ import annotations

import re
from collections import Counter

from .models import KnowledgeClaim, SourceDocument

STOPWORDS = {
    "about", "after", "again", "also", "because", "before", "between", "could", "from", "have", "into", "more", "most",
    "other", "over", "should", "than", "that", "their", "there", "these", "this", "through", "under", "when", "where",
    "which", "while", "with", "would", "一个", "进行", "以及", "通过", "用户", "知识", "功能", "文件", "操作", "框架",
}
SENTENCE_RE = re.compile(r"(?<=[。！？.!?])\s+|\n+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}")
HEADING_RE = re.compile(r"^(#{1,6})\s+(?P<title>.+)$")


def distill_claims(document: SourceDocument, max_claims: int = 40) -> list[KnowledgeClaim]:
    """Extract source-grounded atomic claims from a document.

    The implementation follows the same pipeline shape as the referenced frameworks:
    normalize input, identify sections, extract semantic units, score them, then emit a
    structured knowledge base rather than preserving full text.
    """

    candidates: list[tuple[str, str, tuple[str, ...], float]] = []
    for section_title, section_text in _iter_sections(document.text):
        section_keywords = _top_keywords(section_text, limit=8)
        for sentence in _iter_sentences(section_text):
            if len(sentence) < 20:
                continue
            keywords = _top_keywords(sentence, limit=6) or section_keywords[:4]
            score = _score_sentence(sentence, keywords, section_keywords)
            candidates.append((section_title, sentence, tuple(keywords), score))

    candidates.sort(key=lambda item: item[3], reverse=True)
    claims: list[KnowledgeClaim] = []
    for index, (section, text, keywords, score) in enumerate(candidates[:max_claims], start=1):
        claim_id = f"K{index:04d}"
        claims.append(
            KnowledgeClaim(
                id=claim_id,
                text=text,
                source_path=str(document.path),
                section=section,
                keywords=keywords,
                confidence=round(min(0.99, max(0.35, score)), 2),
            )
        )
    return claims


def _iter_sections(text: str) -> list[tuple[str, str]]:
    current = "Document"
    chunks: dict[str, list[str]] = {current: []}
    for line in text.splitlines():
        match = HEADING_RE.match(line.strip())
        if match:
            current = match.group("title").strip()
            chunks.setdefault(current, [])
            continue
        chunks.setdefault(current, []).append(line)
    return [(title, "\n".join(lines).strip()) for title, lines in chunks.items() if "\n".join(lines).strip()]


def _iter_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for piece in SENTENCE_RE.split(text):
        cleaned = re.sub(r"\s+", " ", piece).strip(" -\t")
        if cleaned:
            sentences.append(cleaned)
    return sentences


def _top_keywords(text: str, limit: int) -> list[str]:
    words = [word.lower() for word in WORD_RE.findall(text)]
    counts = Counter(word for word in words if word not in STOPWORDS)
    return [word for word, _ in counts.most_common(limit)]


def _score_sentence(sentence: str, keywords: tuple[str, ...] | list[str], section_keywords: list[str]) -> float:
    length_score = min(len(sentence) / 240, 0.35)
    keyword_score = min(len(set(keywords) & set(section_keywords)) * 0.12, 0.36)
    structure_score = 0.15 if any(marker in sentence for marker in ("SHALL", "必须", "需要", "支持", "实现", "because", "therefore")) else 0.05
    return 0.3 + length_score + keyword_score + structure_score
