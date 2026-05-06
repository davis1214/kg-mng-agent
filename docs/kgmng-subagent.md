# Knowledge Management Subagent

This subagent fuses four framework patterns into one CLI workflow without inventing an unrelated pipeline:

- **BMAD-style structured knowledge base**: every run writes persistent state under `.kgmng/knowledge/<document>/<sha>/` with manifest, report, graph, and spec artifacts.
- **Graphify-style graph consolidation**: distilled claims become typed graph nodes connected to sections and keywords, with simple communities grouped by section.
- **OpenSpec-style executable requirements**: the active behavior contract is rendered as `spec.md` beside each archived result.
- **SpecKit-style lifecycle**: the CLI follows a predictable lifecycle of clarify intent through the spec, plan/run the pipeline, validate duplicates, and emit reusable artifacts.

## Three-layer architecture

1. **Data layer**: reads raw `.pdf`, `.md`, `.txt`, and `.docx` files into normalized text.
2. **Processing layer**: performs source-grounded distillation, graph building, and preventive deduplication.
3. **Application layer**: exposes the result through `kgmng run <file>`, Markdown reports, JSON graphs, and manifests.

## CLI usage

```bash
kgmng run path/to/document.md
kgmng run path/to/document.pdf --output-dir .kgmng/knowledge --json
kgmng formats
```

PDF and DOCX parsing are optional extras because those formats need third-party readers:

```bash
pip install kg-mng-agent[pdf]
pip install kg-mng-agent[docx]
```
