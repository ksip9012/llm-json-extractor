import pytest
from google.genai import types

from llm_json_extractor.schema_convert import (
    UnsupportedSchemaError,
    to_gemini_schema,
)


def _prop(schema: types.Schema, name: str) -> types.Schema:
    """オブジェクト型の Schema から、プロパティ name の Schema を取り出す。"""
    assert schema.properties is not None
    return schema.properties[name]


def _items(schema: types.Schema) -> types.Schema:
    """配列型の Schema から、要素の Schema を取り出す。"""
    assert schema.items is not None
    return schema.items


def test_converts_plain_string_and_boolean_properties():
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "タイトル"},
            "done": {"type": "boolean", "description": "完了したか"},
        },
        "required": ["title", "done"],
    }

    result = to_gemini_schema(schema)

    assert result.type == types.Type.OBJECT
    assert _prop(result, "title").type == types.Type.STRING
    assert _prop(result, "title").description == "タイトル"
    assert _prop(result, "done").type == types.Type.BOOLEAN
    assert result.required == ["title", "done"]
    assert result.property_ordering == ["title", "done"]


def test_converts_nullable_string_type_array():
    schema = {
        "type": "object",
        "properties": {
            "due_date": {
                "type": ["string", "null"],
                "format": "date",
                "description": "締切日",
            },
        },
        "required": ["due_date"],
    }

    result = to_gemini_schema(schema)

    prop = _prop(result, "due_date")
    assert prop.type == types.Type.STRING
    assert prop.nullable is True
    assert prop.description is not None
    assert "YYYY-MM-DD" in prop.description


def test_converts_array_of_strings():
    schema = {
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

    result = to_gemini_schema(schema)

    prop = _prop(result, "items")
    assert prop.type == types.Type.ARRAY
    assert _items(prop).type == types.Type.STRING


def test_converts_array_of_objects():
    schema = {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "priority": {"type": ["string", "null"]},
                    },
                    "required": ["text", "priority"],
                },
            },
        },
        "required": ["tasks"],
    }

    result = to_gemini_schema(schema)

    item_schema = _items(_prop(result, "tasks"))
    assert item_schema.type == types.Type.OBJECT
    assert _prop(item_schema, "text").type == types.Type.STRING
    assert _prop(item_schema, "priority").nullable is True


def test_carries_over_enum_values():
    schema = {
        "type": "object",
        "properties": {
            "mood": {
                "type": "string",
                "enum": ["good", "neutral", "bad"],
            },
        },
        "required": ["mood"],
    }

    result = to_gemini_schema(schema)

    assert _prop(result, "mood").enum == ["good", "neutral", "bad"]


@pytest.mark.parametrize(
    "prop_schema",
    [
        {"type": "null"},
        {"type": ["null"]},
        {"type": ["string", "integer"]},
        {"anyOf": [{"type": "string"}, {"type": "integer"}]},
        {"oneOf": [{"type": "string"}]},
        {"allOf": [{"type": "string"}]},
        {"$ref": "#/$defs/name"},
        {"type": "array", "items": {"type": "null"}},
        {"type": "object", "properties": {"a": {"anyOf": []}}},
    ],
)
def test_raises_clear_error_for_unsupported_schema(prop_schema):
    schema = {"type": "object", "properties": {"value": prop_schema}}

    with pytest.raises(UnsupportedSchemaError):
        to_gemini_schema(schema)


def test_raises_clear_error_for_unsupported_keyword_at_top_level():
    with pytest.raises(UnsupportedSchemaError, match="anyOf"):
        to_gemini_schema({"anyOf": [{"type": "object"}]})
