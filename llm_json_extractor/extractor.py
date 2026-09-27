"""設計された JSON Schema に従い、Gemini API の Structured Output で
自由入力メモから構造化データを抽出するモジュール（decisions/0004 参照）。"""

import json
import os
from typing import Any

from google import genai
from google.genai import types

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

_PROMPT_TEMPLATE = (
    "次のメモの内容を、指定されたスキーマに従って構造化してください。\n"
    "メモ:\n{note}"
)


def extract_data(
    note: str,
    schema: types.Schema,
    *,
    client: genai.Client | None = None,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """メモ本文を、指定された Gemini Schema に従って構造化データに変換する。

    Args:
        note: 自由入力のメモ本文。
        schema: 抽出結果が従うべき Gemini Schema
            （`schema_convert.to_gemini_schema` の戻り値）。
        client: 使用する genai.Client。省略時は環境変数から生成する。
            テストではモッククライアントを注入する。
        model: 使用するモデル名。

    Returns:
        schema の各プロパティに対応する値を持つ辞書。
    """
    client = client or genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=_PROMPT_TEMPLATE.format(note=note),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )
    return json.loads(response.text)
