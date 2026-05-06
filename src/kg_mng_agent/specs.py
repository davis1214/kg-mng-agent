"""Spec-driven contracts used by the processing layer.

This module keeps the agent aligned with OpenSpec/SpecKit-style workflows: intent is
captured as explicit requirements and scenarios before processing starts.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Requirement:
    """A behavior the knowledge-management agent must satisfy."""

    name: str
    shall: str
    scenario: str


KNOWLEDGE_SPEC = (
    Requirement(
        name="Source-grounded distillation",
        shall="The agent SHALL extract atomic claims traceable to the source file and section.",
        scenario="GIVEN a supported document WHEN distillation runs THEN every claim records source, section, keywords, and confidence.",
    ),
    Requirement(
        name="Graph-structured consolidation",
        shall="The agent SHALL build entity and claim relationships before archival.",
        scenario="GIVEN distilled claims WHEN graph building runs THEN claims, keywords, and sections are connected by typed edges.",
    ),
    Requirement(
        name="Preventive duplicate control",
        shall="The agent SHALL remove exact and near-duplicate knowledge claims before writing the archive.",
        scenario="GIVEN similar claims WHEN deduplication runs THEN the archive keeps the highest-quality claim and records the decision.",
    ),
    Requirement(
        name="Lifecycle archive",
        shall="The agent SHALL produce durable manifest, report, and graph artifacts for each run.",
        scenario="GIVEN a completed run WHEN archival runs THEN human-readable and machine-readable outputs are written under the knowledge base.",
    ),
)


def render_spec_markdown() -> str:
    """Render the active behavior contract as OpenSpec-compatible Markdown."""

    lines = ["# Knowledge Management Agent Specification", "", "## Purpose", "", "Unify document distillation, graph consolidation, deduplication, and archival into a single CLI-driven subagent.", "", "## Requirements"]
    for requirement in KNOWLEDGE_SPEC:
        lines.extend(
            [
                "",
                f"### Requirement: {requirement.name}",
                "",
                requirement.shall,
                "",
                "#### Scenario: CLI execution",
                "",
                f"- {requirement.scenario}",
            ]
        )
    lines.append("")
    return "\n".join(lines)
