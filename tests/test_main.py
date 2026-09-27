"""CLI のテスト。`genai.Client` をモックに差し替え、実 API は呼ばない
（decisions/0006 参照）。"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from llm_json_extractor.__main__ import main

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_notes"
)

_SCHEMA = {
    "type": "object",
    "properties": {"summary": {"type": "string"}},
    "required": ["summary"],
}
_DATA = {"summary": "テスト用の要約"}


class _FakeModels:
    def generate_content(self, *, model, contents, config):
        if config.response_schema is None:
            return SimpleNamespace(text=json.dumps(_SCHEMA))
        return SimpleNamespace(text=json.dumps(_DATA))


class _FakeClient:
    def __init__(self, *args, **kwargs):
        self.models = _FakeModels()


def test_main_prints_json_array_for_folder(monkeypatch, capsys):
    monkeypatch.setattr(
        "llm_json_extractor.schema_designer.genai.Client", _FakeClient
    )
    monkeypatch.setattr(
        "llm_json_extractor.extractor.genai.Client", _FakeClient
    )
    monkeypatch.setattr(
        "sys.argv", ["llm_json_extractor", str(FIXTURES_DIR)]
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert len(output) == 7
    assert {item["file_name"] for item in output} == {
        p.name for p in FIXTURES_DIR.iterdir()
    }


def test_main_exits_with_error_for_missing_folder(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv", ["llm_json_extractor", "no-such-folder"]
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert "no-such-folder" in capsys.readouterr().err
