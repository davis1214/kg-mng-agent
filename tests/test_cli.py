from __future__ import annotations

import json
from pathlib import Path

from kg_mng_agent.cli import main


def test_cli_run_json(tmp_path: Path, capsys) -> None:
    source = tmp_path / "notes.txt"
    source.write_text(
        "The agent SHALL distill important knowledge from plain text documents.\n"
        "The archive stores a manifest and graph for future knowledge services.\n",
        encoding="utf-8",
    )

    exit_code = main(["run", str(source), "--output-dir", str(tmp_path / "out"), "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["claims"] >= 1
    assert Path(payload["report"]).exists()


def test_cli_formats(capsys) -> None:
    assert main(["formats"]) == 0
    assert ".pdf" in capsys.readouterr().out
