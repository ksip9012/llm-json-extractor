"""自由入力のメモから、その内容に適した JSON Schema を設計させるモジュール
（decisions/0004 の1段階目）。"""

import json
import os
from typing import Any

from google import genai
from google.genai import types

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

_PROMPT_TEMPLATE = """\
次の自由入力のメモを分析し、その内容を構造化するのに最も適した
JSON Schema（draft 2020-12のサブセットでよい）を設計してください。

制約:
- 出力は JSON Schema オブジェクト自体（"type": "object"、"properties"、
  "required" を持つ）のみとし、それ以外の説明文は含めない
- 各プロパティには、そのメモ内容に基づいた具体的な description をつける
- 使用してよい type は string, integer, number, boolean, object, array のみ
- メモの内容に本当に必要な項目だけを含め、過剰に細分化しない

メモ:
{note}
"""


def design_schema(
    note: str,
    *,
    client: genai.Client | None = None,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """自由入力のメモに適した JSON Schema を設計する。

    `response_schema` による制約は与えず、`response_mime_type` のみで
    JSON 出力を強制する（decisions/0004 参照）。

    Args:
        note: 自由入力のメモ本文。
        client: 使用する genai.Client。省略時は環境変数から生成する。
            テストではモッククライアントを注入する。
        model: 使用するモデル名。

    Returns:
        `properties` / `required` を持つオブジェクト型の JSON Schema。
    """
    client = client or genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=_PROMPT_TEMPLATE.format(note=note),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)
