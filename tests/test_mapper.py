"""mapper のテスト。Gemini API は呼ばず、`config.response_schema` の有無で
スキーマ設計呼び出し/データ抽出呼び出しを判定するモッククライアントを使う
（decisions/0006 参照）。"""

import json
from pathlib import Path
from dataclasses import dataclass

import pytest
from google.genai import errors
from jsonschema.exceptions import ValidationError

from llm_json_extractor.mapper import map_folder, map_note

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_notes"
)


@dataclass
class _FakeResponse:
    text: str | None


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
            return _FakeResponse(text=json.dumps(self.schema))
        return _FakeResponse(text=json.dumps(self.data))


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

    result = map_note(FIXTURES_DIR / "shopping_list.txt", client=fake_client)

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


@pytest.mark.parametrize(
    "failure",
    [
        errors.ServerError(
            503,
            {"error": {"code": 503, "message": "x", "status": "UNAVAILABLE"}},
        ),
        _FakeResponse(text=None),
        _FakeResponse(text="not json"),
        _FakeResponse(text='{"type": "no-such-type"}'),
    ],
    ids=["api_error", "empty", "invalid_json", "invalid_schema"],
)
def test_map_folder_records_error_and_continues(failure):
    class _Models(_TwoStepFakeModels):
        def generate_content(self, *, model, contents, config):
            if "牛乳" not in contents:
                return super().generate_content(
                    model=model, contents=contents, config=config
                )
            if isinstance(failure, Exception):
                raise failure
            return failure

    class _Client:
        models = _Models(_SHOPPING_SCHEMA, _SHOPPING_DATA)

    results = map_folder(FIXTURES_DIR, client=_Client())

    assert len(results) == 7
    failed = [r for r in results if "error" in r]
    assert [r["file_name"] for r in failed] == ["shopping_list.txt"]
    assert set(failed[0]) == {"file_name", "error"}


def test_map_folder_records_data_that_does_not_conform_to_schema():
    fake_client = _TwoStepFakeClient(_SHOPPING_SCHEMA, {"items": "牛乳"})

    results = map_folder(FIXTURES_DIR, client=fake_client)

    assert len(results) == 7
    assert all("error" in r for r in results)


def test_map_note_creates_clients_with_retry_options(monkeypatch):
    created = []

    def fake_client_factory(**kwargs):
        created.append(kwargs)
        return _TwoStepFakeClient(_SHOPPING_SCHEMA, _SHOPPING_DATA)

    monkeypatch.setattr(
        "llm_json_extractor.schema_designer.genai.Client", fake_client_factory
    )
    monkeypatch.setattr(
        "llm_json_extractor.extractor.genai.Client", fake_client_factory
    )

    map_note(FIXTURES_DIR / "shopping_list.txt")

    assert len(created) == 2
    assert all(c["http_options"].retry_options is not None for c in created)
