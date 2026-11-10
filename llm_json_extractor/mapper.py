"""自由入力メモから、内容に適した JSON Schema の設計とデータ抽出を
組み合わせて構造化するモジュール。"""

from pathlib import Path
from typing import Any

import httpx
from google.genai import errors
from jsonschema import (
    Draft202012Validator,
    SchemaError,
    ValidationError,
    validate,
)

from llm_json_extractor.extractor import extract_data
from llm_json_extractor.file_lister import list_files, read_note
from llm_json_extractor.llm_client import LLMClient
from llm_json_extractor.schema_convert import to_gemini_schema
from llm_json_extractor.schema_designer import design_schema

# 1件のメモの失敗として記録し、次のメモに進むエラー
# （API のエラー、通信のエラー、スキーマの不備や違反、応答が空・JSON でない）
_NOTE_ERRORS = (
    errors.APIError,
    httpx.TransportError,
    SchemaError,
    ValidationError,
    ValueError,
)


def map_note(
    path: str | Path, *, client: LLMClient | None = None
) -> dict[str, Any]:
    """1件の自由入力メモを、LLM が設計したスキーマに基づいて構造化する。

    設計されたスキーマ自体が妥当な JSON Schema であること、抽出された
    データがそのスキーマに従っていることの両方を検証する（decisions/0005）。

    Args:
        path: 対象メモファイルのパス。
        client: `design_schema` / `extract_data` に渡すクライアント。

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
    folder: str | Path, *, client: LLMClient | None = None
) -> list[dict[str, Any]]:
    """フォルダ直下にあるメモを、それぞれ構造化した辞書のリストを取得する。

    1件の失敗では止まらず、失敗したメモは `file_name` と `error` だけを
    持つ辞書としてリストに残す。

    Args:
        folder: 対象フォルダのパス。
        client: `map_note` に渡すクライアント。

    Returns:
        `map_note` の戻り値（失敗したメモはエラーの辞書）を
        ファイル名の昇順に並べたリスト。
    """
    folder_path = Path(folder)
    results: list[dict[str, Any]] = []
    for name in list_files(folder_path):
        try:
            results.append(map_note(folder_path / name, client=client))
        except _NOTE_ERRORS as error:
            message = str(error).splitlines()[0] if str(error) else ""
            results.append(
                {
                    "file_name": name,
                    "error": f"{type(error).__name__}: {message}",
                }
            )
    return results
