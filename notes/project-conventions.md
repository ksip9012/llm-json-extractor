# llm-json-extractor 開発規約

個人プロジェクト共通の型（`~/documents/life/gtd/002_project/20260720_個人プロジェクト/common_template.md`）を元に、このプロジェクト用に調整したもの。Step1-A1・A2 の規約をそのまま踏襲している。

---

## 1. README 構成（ポートフォリオ向け）

1. タイトル・一言概要
2. デモ
3. 背景・課題
4. 主な機能
5. アーキテクチャ図・技術スタック一覧
6. 技術選定理由（`decisions/` の ADR にリンク）
7. セットアップ手順
8. 使い方
9. テストの実行方法
10. 今後の展望・既知の制約

---

## 2. テスト方針

- 主要ロジック（スキーマ変換など）には単体テストを書く
- Gemini API への実呼び出しは自動テストに含めない。モッククライアントで
  応答を固定する（[decisions/0006](../decisions/0006-mock-llm-responses-in-tests.md)）
- `pytest` を基本とする

---

## 3. Design Decision（ADR）運用ルール

- 形式: 軽量 ADR。1 決定 = 1 ファイル
- 置き場所: プロジェクト直下の `decisions/` ディレクトリ
- ファイル名: `NNNN-短いタイトル.md`
- Status の種類: `Proposed` / `Accepted` / `Deprecated` / `Superseded by NNNN`
- テンプレートは `decisions/0000-template.md` に置いてある

---

## 4. デプロイ・公開方針の判断基準

Step1-A1・A2 と同様、「GitHub 公開まで」を基本方針とする。実装が一定形になった段階で Private → Public に切り替える。

---

## この文書自体の位置づけ

個人プロジェクト共通の型・Step1-A1/A2 の規約からこのプロジェクト用にコピー・調整したもの。
