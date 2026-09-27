"""schema_designer のテスト。実 API は呼ばず、モッククライアントで
リクエスト内容・レスポンス解釈を検証する（decisions/0006 参照）。"""

import json
from types import SimpleNamespace

from llm_json_extractor.schema_designer import design_schema

_CANNED_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["items"],
}


class _FakeModels:
    def __init__(self, response_text):
        self.response_text = response_text
        self.calls = []

    def generate_content(self, *, model, contents, config):
        self.calls.append(
            {"model": model, "contents": contents, "config": config}
        )
        return SimpleNamespace(text=self.response_text)


class _FakeClient:
    def __init__(self, response_text):
        self.models = _FakeModels(response_text)


def test_design_schema_parses_json_response():
    fake_client = _FakeClient(json.dumps(_CANNED_SCHEMA))

    result = design_schema("牛乳\n卵", client=fake_client)

    assert result == _CANNED_SCHEMA


def test_design_schema_does_not_constrain_response_schema():
    fake_client = _FakeClient(json.dumps(_CANNED_SCHEMA))

    design_schema("牛乳\n卵", client=fake_client)

    call = fake_client.models.calls[0]
    assert call["config"].response_schema is None
    assert call["config"].response_mime_type == "application/json"


def test_design_schema_includes_note_in_prompt():
    fake_client = _FakeClient(json.dumps(_CANNED_SCHEMA))

    design_schema("牛乳\n卵", client=fake_client)

    assert "牛乳" in fake_client.models.calls[0]["contents"]
