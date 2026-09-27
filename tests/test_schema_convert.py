from google.genai import types

from llm_json_extractor.schema_convert import to_gemini_schema


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
    assert result.properties["title"].type == types.Type.STRING
    assert result.properties["title"].description == "タイトル"
    assert result.properties["done"].type == types.Type.BOOLEAN
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

    prop = result.properties["due_date"]
    assert prop.type == types.Type.STRING
    assert prop.nullable is True
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

    prop = result.properties["items"]
    assert prop.type == types.Type.ARRAY
    assert prop.items.type == types.Type.STRING


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

    item_schema = result.properties["tasks"].items
    assert item_schema.type == types.Type.OBJECT
    assert item_schema.properties["text"].type == types.Type.STRING
    assert item_schema.properties["priority"].nullable is True


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

    assert result.properties["mood"].enum == ["good", "neutral", "bad"]
