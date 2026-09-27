"""mapper のテスト。Gemini API は呼ばず、`config.response_schema` の有無で
スキーマ設計呼び出し/データ抽出呼び出しを判定するモッククライアントを使う
（decisions/0006 参照）。"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema.exceptions import ValidationError

from llm_json_extractor.mapper import map_folder, map_note

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_notes"
)


class _TwoStepFakeModels:
    def __init__(self, schema, data):
        self.schema = schema
        self.data = data
        self.calls = []

    def generate_content(self, *, model, contents, config):
        self.calls.append(
            {"model": model, "contents": contents, "config": config}
        )
        if config.response_schema is None:
            return SimpleNamespace(text=json.dumps(self.schema))
        return SimpleNamespace(text=json.dumps(self.data))


class _TwoStepFakeClient:
    def __init__(self, schema, data):
        self.models = _TwoStepFakeModels(schema, data)


_SHOPPING_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "買い物リストの品目",
        },
    },
    "required": ["items"],
}

_SHOPPING_DATA = {
    "items": ["牛乳", "卵 1パック", "食パン", "バナナ 3本"],
}


def test_map_note_returns_schema_and_data_for_shopping_list():
    fake_client = _TwoStepFakeClient(_SHOPPING_SCHEMA, _SHOPPING_DATA)

    result = map_note(
        FIXTURES_DIR / "shopping_list.txt", client=fake_client
    )

    assert result["file_name"] == "shopping_list.txt"
    assert result["schema"] == _SHOPPING_SCHEMA
    assert result["data"] == _SHOPPING_DATA


def test_map_note_calls_schema_design_before_extraction():
    fake_client = _TwoStepFakeClient(_SHOPPING_SCHEMA, _SHOPPING_DATA)

    map_note(FIXTURES_DIR / "shopping_list.txt", client=fake_client)

    calls = fake_client.models.calls
    assert len(calls) == 2
    assert calls[0]["config"].response_schema is None
    assert calls[1]["config"].response_schema is not None


def test_map_note_raises_when_data_does_not_conform_to_schema():
    invalid_data = {"items": "牛乳"}  # 配列であるべきなのに文字列
    fake_client = _TwoStepFakeClient(_SHOPPING_SCHEMA, invalid_data)

    with pytest.raises(ValidationError):
        map_note(FIXTURES_DIR / "shopping_list.txt", client=fake_client)


def test_map_folder_returns_all_files_sorted_by_name():
    fake_client = _TwoStepFakeClient(_SHOPPING_SCHEMA, _SHOPPING_DATA)

    results = map_folder(FIXTURES_DIR, client=fake_client)

    assert [r["file_name"] for r in results] == sorted(
        r["file_name"] for r in results
    )
    assert len(results) == 7
