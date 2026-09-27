# 0003. LLM プロバイダ・認証は Step1-A2 の構成を再利用する

- Status: Accepted
- Date: 2026-09-27

## Context
Step1-A2（llm-structured-output-extractor）で、Gemini API へのアクセス方法を
以下のように確立済み。

- AI Studio の API キーではなく、Vertex AI（GCP プロジェクト
  `test-adk-479704`、`location=global`）経由で認証する
  （[llm-structured-output-extractor/decisions/0005](https://github.com/ksip9012/llm-structured-output-extractor/blob/main/decisions/0005-use-vertex-ai-auth.md)）
- モデルは `gemini-3.8-flash`
  （[同 0007](https://github.com/ksip9012/llm-structured-output-extractor/blob/main/decisions/0007-upgrade-to-gemini-3-8-flash.md)）

この構成は billing・モデル提供状況の調査を経て確定したものであり、
Step1-B で同じ調査をやり直す理由はない。

## Decision
Step1-B でも同じ Vertex AI 構成（プロジェクト・`location=global`・
`gemini-3.8-flash`）を初期値として使う。

```bash
gcloud auth application-default login

export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=test-adk-479704
export GOOGLE_CLOUD_LOCATION=global
```

## Consequences
- Step1-A2 で得た知見（billing・モデル可用性）をそのまま活かせる
- Step1-A2 とは別リポジトリのため、コードの直接 import はできず、
  `gemini_client.py` 相当のロジックは重複実装になる
- 今後 Vertex AI 側のモデル提供状況が変わった場合、Step1-A2・Step1-B
  それぞれで個別に ADR を起票して追随する必要がある
