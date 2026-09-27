"""extractor のテスト。実 API は呼ばず、モッククライアントでリクエスト内容・
レスポンス解釈を検証する（decisions/0006 参照）。"""

from types import SimpleNamespace

from google.genai import types

from llm_json_extractor.extractor import extract_data

_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "items": types.Schema(
            type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)
        ),
    },
    required=["items"],
)


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


def test_extract_data_parses_json_response():
    fake_client = _FakeClient('{"items": ["牛乳", "卵"]}')

    result = extract_data("牛乳\n卵", _SCHEMA, client=fake_client)

    assert result == {"items": ["牛乳", "卵"]}


def test_extract_data_passes_note_and_schema_to_client():
    fake_client = _FakeClient('{"items": ["牛乳", "卵"]}')

    extract_data("牛乳\n卵", _SCHEMA, client=fake_client)

    call = fake_client.models.calls[0]
    assert "牛乳" in call["contents"]
    assert call["config"].response_schema is _SCHEMA
    assert call["config"].response_mime_type == "application/json"
