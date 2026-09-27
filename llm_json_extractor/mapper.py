"""自由入力メモから、内容に適した JSON Schema の設計とデータ抽出を
組み合わせて構造化するモジュール。"""

from pathlib import Path
from typing import Any

from google import genai
from jsonschema import Draft202012Validator, validate

from llm_json_extractor.extractor import extract_data
from llm_json_extractor.file_lister import list_files, read_note
from llm_json_extractor.schema_convert import to_gemini_schema
from llm_json_extractor.schema_designer import design_schema


def map_note(
    path: str | Path, *, client: genai.Client | None = None
) -> dict[str, Any]:
    """1件の自由入力メモを、LLM が設計したスキーマに基づいて構造化する。

    設計されたスキーマ自体が妥当な JSON Schema であること、抽出された
    データがそのスキーマに従っていることの両方を検証する（decisions/0005）。

    Args:
        path: 対象メモファイルのパス。
        client: `design_schema` / `extract_data` に渡す genai.Client。

    Returns:
        `file_name` / `schema`（LLM が設計した JSON Schema）/
        `data`（そのスキーマに従って抽出された構造化データ）を持つ辞書。
    """
    path_obj = Path(path)
    note = read_note(path_obj)

    schema = design_schema(note, client=client)
    Draft202012Validator.check_schema(schema)

    gemini_schema = to_gemini_schema(schema)
    data = extract_data(note, gemini_schema, client=client)
    validate(instance=data, schema=schema)

    return {
        "file_name": path_obj.name,
        "schema": schema,
        "data": data,
    }


def map_folder(
    folder: str | Path, *, client: genai.Client | None = None
) -> list[dict[str, Any]]:
    """フォルダ直下にあるメモを、それぞれ構造化した辞書のリストを取得する。

    Args:
        folder: 対象フォルダのパス。
        client: `map_note` に渡す genai.Client。

    Returns:
        `map_note` の戻り値をファイル名の昇順に並べたリスト。
    """
    folder_path = Path(folder)
    return [
        map_note(folder_path / name, client=client)
        for name in list_files(folder_path)
    ]
