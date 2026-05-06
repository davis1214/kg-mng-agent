# kg-mng-agent

`kg-mng-agent` is a CLI-driven knowledge-management subagent for distilling, deduplicating, graphing, and archiving knowledge from `.pdf`, `.md`, `.txt`, and `.docx` files.

It intentionally follows the requested framework lineage:

- BMAD: structured persistent knowledge archive.
- Graphify: graph-first consolidation of claims, keywords, sections, and communities.
- OpenSpec: explicit requirements/spec artifacts generated with each run.
- SpecKit: repeatable lifecycle from specification to validation to reusable artifacts.

## Install for development

```bash
python -m pip install -e .
```

Optional readers:

```bash
python -m pip install -e '.[pdf,docx]'
```

## Usage

```bash
kgmng run ./notes.md
kgmng run ./paper.pdf --json
kgmng formats
```

The default archive location is `.kgmng/knowledge/<document-stem>/<sha-prefix>/` and contains:

- `manifest.json` — source metadata, lifecycle counts, and generated artifact names.
- `distilled.md` — distilled claims, duplicate-review log, and graph summary.
- `graph.json` — typed nodes, edges, and section communities.
- `spec.md` — OpenSpec-compatible behavior contract for the run.

## Development checks

```bash
python -m pytest
python -m kg_mng_agent.cli formats
```
