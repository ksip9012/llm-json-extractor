# 0001. 開発言語に Python を採用する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A1（json-schema-mapper）・Step1-A2（llm-structured-output-extractor）
に続く Step1 シリーズ最後のプロジェクト。LLM API 呼び出し・JSON 検証まわりの
実装パターンは Step1-A2 でほぼ確立している。

## Decision
Step1-A1・A2 に続き、開発言語には Python を採用する。

## Consequences
- Step1-A2 の Gemini API 呼び出し・pytest 運用パターンをほぼそのまま流用できる
- 技術スタックは「プロジェクトごとに最適なものを選定する」（common_template 方針）
  が前提のため、他プロジェクトで異なる言語を選ぶことは妨げない
