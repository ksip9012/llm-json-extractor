# 0005. 生成されたスキーマ自体と、データとの整合性の両方を検証する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A1・A2 では固定の `schema.json` があったため、
「抽出結果がその schema.json に従っているか」を `jsonschema.validate()`
一発で検証できた。Step1-B ではスキーマ自体が入力ごとに LLM が設計するため、
検証すべきことが2種類に分かれる（[0002](./0002-use-diverse-personal-memos-as-input.md)
で先送りにしていた論点）。

1. LLM が設計したスキーマ自体が、そもそも妥当な JSON Schema か
2. LLM が抽出したデータが、その（LLM自身が設計した）スキーマに従っているか

## Decision
両方を検証する。

1. `Draft202012Validator.check_schema(designed_schema)` で、設計された
   スキーマ自体が構文的に妥当な JSON Schema であることを検証する
2. `jsonschema.validate(instance=extracted_data, schema=designed_schema)` で、
   抽出されたデータが、その設計されたスキーマに従っていることを検証する

どちらかが失敗した場合は例外を送出し、`map_file` の戻り値としては返さない
（Step1-A1・A2 と同様、検証を通った結果のみを返す）。

## Consequences
- 「LLM が一貫した仕事をしたか」（設計したスキーマと実際の抽出結果が
  食い違っていないか）を機械的に検知できる。これは固定スキーマの
  Step1-A2 にはなかった、Step1-B 特有の検証観点
- 検証に失敗するケース（LLM がスキーマ通りにデータを埋められなかった等）を
  実装時に実際に観測したら、その頻度・原因は notes に記録する
- スキーマの「意味的な妥当性」（設計されたスキーマがそのメモの内容を
  表現するのに本当に適切か）までは自動検証できない。これは人間が
  README・notes でのレビューで確認する
