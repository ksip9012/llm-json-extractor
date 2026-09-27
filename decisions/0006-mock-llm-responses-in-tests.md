# 0006. 自動テストでは LLM 応答をモックする

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A2（[decisions/0004](https://github.com/ksip9012/llm-structured-output-extractor/blob/main/decisions/0004-mock-llm-responses-in-tests.md)）
と同じ理由（費用・非決定性・API障害時のテスト失敗・実行速度）により、
自動テストで実 API を呼びたくない。

Step1-B は1回の `map_note` の中で Gemini を2回呼ぶ
（[0004](./0004-two-step-schema-design-and-extraction.md)）ため、
モッククライアントは「スキーマ設計の呼び出し」と「データ抽出の呼び出し」を
区別して別々の応答を返す必要がある。

## Decision
自動テストでは、`config.response_schema` の有無でどちらの呼び出しかを
判定するモッククライアントを使い、実 API は呼ばない。

- `response_schema` が無い呼び出し → スキーマ設計呼び出しとみなし、
  あらかじめ用意した JSON Schema を返す
- `response_schema` がある呼び出し → データ抽出呼び出しとみなし、
  あらかじめ用意したデータを返す

実 API との疎通確認は、Step1-A2 と同様に手動実行で行う。

## Consequences
- 通常のテストは無料・高速・決定的になる
- モックの応答（スキーマ・データ）は手作業で用意するため、実際の Gemini の
  挙動（スキーマ設計の癖など）を反映できているとは限らない。実際の挙動は
  notes に別途記録する
