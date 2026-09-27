# 0004. スキーマ設計と抽出を2段階の LLM 呼び出しに分ける

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A2 では、固定の `schema.json` を Gemini の `response_schema` に変換して
渡し、その制約のもとでデータを抽出していた。Step1-B では固定スキーマがなく、
「入力に対してどんな JSON 構造が適切か」自体を LLM に考えさせる必要がある
（[0002](./0002-use-diverse-personal-memos-as-input.md)）。

候補は大きく2つあった。

1. **1回の呼び出し**で `{"schema": {...}, "data": {...}}` のような形を
   一度に出力させる
2. **2回の呼び出し**に分ける: (1) 自由入力からその内容に適した
   JSON Schema を設計させる → (2) 設計されたスキーマを Gemini の
   `response_schema` に変換し、そのスキーマに従ってデータを抽出させる

## Decision
2段階の呼び出しに分ける。

1. `schema_designer.py`: メモのテキストを渡し、`response_schema` による
   制約なし（`response_mime_type: application/json` のみ）で、
   その内容に適した JSON Schema（draft 2020-12 のサブセット）を設計させる
2. `schema_convert.py`: 設計されたスキーマを Gemini の `response_schema`
   （OpenAPI 3.0 サブセット）に変換する。Step1-A2 の変換ロジックを踏襲しつつ、
   `array` 型（`items` を持つ）にも対応させる（自由入力では配列項目が
   自然に発生するため）
3. `extractor.py`: 変換したスキーマを `response_schema` として渡し、
   Step1-A2 と同じ Structured Output の仕組みでデータを抽出する

## Consequences
- Step1-A2 で確立した「スキーマを Gemini の response_schema に変換し、
  制約付きで抽出する」という技術をそのまま2段階目に再利用できる
- LLM が設計したスキーマ自体（1段階目の出力）を保存・検証対象にできるため、
  「LLM が設計したスキーマにLLM自身の抽出結果が従っているか」という
  Step1-B 特有の検証観点が生まれる（[0005](./0005-validate-against-designed-schema.md) 参照）
- API 呼び出しが2回になるため、1回で済ませる案に比べてレイテンシ・コストは増える。
  個人の学習プロジェクトの実行頻度では問題にならないと判断し、精度・設計の
  分かりやすさを優先する
