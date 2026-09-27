# llm-json-extractor

自由入力のメモを渡すと、その内容に適した JSON Schema を LLM 自身に設計させた上で、そのスキーマに従って構造化データを抽出するツール。Step1（構造化された出力の制御）シリーズの最終段階（Step1-B）で、Step1-A1（[json-schema-mapper](https://github.com/ksip9012/json-schema-mapper)、ルールベース）・Step1-A2（[llm-structured-output-extractor](https://github.com/ksip9012/llm-structured-output-extractor)、固定スキーマ + LLM）に続き、スキーマ自体を LLM に考えさせる点が異なる。

## デモ

Vertex AI 経由・`gemini-3.8-flash`（[decisions/0003](./decisions/0003-reuse-gemini-vertex-ai-setup.md)）で実際に動作確認済み。買い物リストのメモに対し、LLM 自身が以下のスキーマを設計し、そのスキーマに従ってデータを抽出した。

```console
$ python -m llm_json_extractor fixtures/sample_notes
[
  {
    "file_name": "shopping_list.txt",
    "schema": {
      "type": "object",
      "properties": {
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "quantity": { "type": "string" },
              "note": { "type": "string" }
            },
            "required": ["name"]
          }
        }
      },
      "required": ["items"]
    },
    "data": {
      "items": [
        { "name": "牛乳" },
        { "name": "卵", "quantity": "1パック" },
        { "name": "コーヒー豆", "note": "できれば深煎り" }
      ]
    }
  },
  ...
]
```

他のメモ（会議メモ・日記・旅行計画など）でどんなスキーマが設計されたかは [notes/schema-design-observations.md](./notes/schema-design-observations.md) にまとめている。

## 背景・課題

「自由入力をどう構造化データに落とし込むか」を学ぶ3ステップの最終段階（Step1-B）。Step1-A1・A2 は「どう抽出するか」が主題だったのに対し、Step1-B は「そもそもどんな構造で表現すべきか」自体を LLM に考えさせる点が異なる（[decisions/0002](./decisions/0002-use-diverse-personal-memos-as-input.md)）。

## 主な機能

- フォルダを指定して実行し（`python -m llm_json_extractor <folder>`）、フォルダ内の全メモを構造化した JSON 配列を標準出力に出力する
- 1件のメモを受け取り、その内容に適した JSON Schema を Gemini API に設計させ（`design_schema()`）、そのスキーマに従ってデータを抽出する（`extract_data()`）という2段階の LLM 呼び出しを組み合わせる（`map_note()`、[decisions/0004](./decisions/0004-two-step-schema-design-and-extraction.md)）
- 設計されたスキーマ自体の妥当性・抽出結果がそのスキーマに従っているかの両方を検証する（[decisions/0005](./decisions/0005-validate-against-designed-schema.md)）
- 自動テストでは実 API を呼ばず、モッククライアントで固定応答を返す（[decisions/0006](./decisions/0006-mock-llm-responses-in-tests.md)）

## アーキテクチャ・技術スタック

- 言語: Python 3.14
- LLM: Google Gemini API（[google-genai](https://pypi.org/project/google-genai/)、Vertex AI 経由）
- スキーマ定義・検証: [jsonschema](https://pypi.org/project/jsonschema/)（JSON Schema draft 2020-12）
- Lint: ruff
- テスト: pytest

モジュール構成:

- [`llm_json_extractor/file_lister.py`](./llm_json_extractor/file_lister.py): フォルダ内のメモファイルの一覧・本文取得
- [`llm_json_extractor/schema_designer.py`](./llm_json_extractor/schema_designer.py): メモの内容に適した JSON Schema を Gemini API に設計させる（1段階目）
- [`llm_json_extractor/schema_convert.py`](./llm_json_extractor/schema_convert.py): 設計された JSON Schema を Gemini の `response_schema`（OpenAPI 3.0 サブセット）に変換する。Step1-A2 の変換ロジックを踏襲し array 型に対応
- [`llm_json_extractor/extractor.py`](./llm_json_extractor/extractor.py): 変換したスキーマに従ってデータを抽出する（2段階目）
- [`llm_json_extractor/mapper.py`](./llm_json_extractor/mapper.py): 上記を組み合わせて実行・検証する（`map_note()` / `map_folder()`）
- [`llm_json_extractor/__main__.py`](./llm_json_extractor/__main__.py): `python -m llm_json_extractor <folder>` の CLI エントリポイント

## 技術選定理由

- [0001](./decisions/0001-use-python.md): 開発言語に Python を採用
- [0002](./decisions/0002-use-diverse-personal-memos-as-input.md): 入力データに多様な形式の短い個人メモを採用
- [0003](./decisions/0003-reuse-gemini-vertex-ai-setup.md): LLM プロバイダ・認証は Step1-A2 の構成を再利用
- [0004](./decisions/0004-two-step-schema-design-and-extraction.md): スキーマ設計と抽出を2段階の LLM 呼び出しに分ける
- [0005](./decisions/0005-validate-against-designed-schema.md): 生成されたスキーマ自体とデータとの整合性の両方を検証する
- [0006](./decisions/0006-mock-llm-responses-in-tests.md): 自動テストでは LLM 応答をモックする

## セットアップ手順

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install google-genai jsonschema pytest ruff
```

Gemini API を実際に呼び出すには、Vertex AI 経由の認証が必要（[decisions/0003](./decisions/0003-reuse-gemini-vertex-ai-setup.md)）。

```bash
gcloud auth application-default login

export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=test-adk-479704
export GOOGLE_CLOUD_LOCATION=global
```

## 使い方

ターミナルから：

```bash
python -m llm_json_extractor <folder>
```

Python から：

```python
from llm_json_extractor.mapper import map_note, map_folder

result = map_note("fixtures/sample_notes/shopping_list.txt")
results = map_folder("fixtures/sample_notes")
```

## テストの実行方法

```bash
pip install google-genai jsonschema pytest ruff
ruff check .
pytest
```

自動テストは Gemini API を実際には呼ばず、モッククライアントで固定応答を返す（[decisions/0006](./decisions/0006-mock-llm-responses-in-tests.md)）。

## 今後の展望・既知の制約

- `fixtures/sample_notes` 全7件で実 API による動作確認を実施済み。全件でスキーマの妥当性・データとの整合性の両方が検証を通過した（詳細: [notes/schema-design-observations.md](./notes/schema-design-observations.md)）
- あえて曖昧にした複合メモ（`mixed_note.txt`）でも、想定したほどの混乱は見られなかった。より曖昧な入力でのロバスト性は追加検証の余地がある
- Step1 シリーズ全体（ルールベース → 固定スキーマ+LLM → 自由スキーマ+LLM）としての精度・コスト・レイテンシの横断比較はまだ行っていない
