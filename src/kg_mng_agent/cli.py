"""Command-line interface for the knowledge-management subagent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import KnowledgeAgent
from .extractors import SUPPORTED_EXTENSIONS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kgmng",
        description="Distill, deduplicate, graph, and archive knowledge from pdf/markdown/txt/docx files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the full knowledge-management pipeline for one file.")
    run_parser.add_argument("file", type=Path, help="Input .pdf, .md, .txt, or .docx file.")
    run_parser.add_argument("--output-dir", type=Path, default=Path(".kgmng/knowledge"), help="Knowledge archive directory.")
    run_parser.add_argument("--max-claims", type=int, default=40, help="Maximum claims to distill before deduplication.")
    run_parser.add_argument("--dedup-threshold", type=float, default=0.82, help="Jaccard threshold for near-duplicate removal.")
    run_parser.add_argument("--json", action="store_true", help="Print machine-readable run summary.")

    subparsers.add_parser("formats", help="List supported input formats.")
    parser.set_defaults(command="run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "formats":
        print("Supported formats: " + ", ".join(sorted(SUPPORTED_EXTENSIONS)))
        return 0

    if not hasattr(args, "file"):
        build_parser().print_help(sys.stderr)
        return 2

    agent = KnowledgeAgent(output_dir=args.output_dir, max_claims=args.max_claims, dedup_threshold=args.dedup_threshold)
    try:
        run = agent.run(args.file)
    except Exception as exc:  # noqa: BLE001 - CLI should convert all pipeline failures into a concise error.
        print(f"kgmng error: {exc}", file=sys.stderr)
        return 1

    summary = {
        "source": str(run.source.path),
        "archive_dir": str(run.archive_dir),
        "claims": len(run.claims),
        "deduped_claims": len(run.deduped_claims),
        "duplicates_removed": len(run.dedup_decisions),
        "report": str(run.report_path),
        "graph": str(run.graph_path),
        "manifest": str(run.manifest_path),
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("Knowledge management run complete")
        for key, value in summary.items():
            print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
