# スキーマ設計フェーズの観察記録（初回検証, 2026-09-27）

`gemini-3.8-flash`（Vertex AI, `location=global`, decisions/0003）で
`fixtures/sample_notes` 全7件を実行し、`map_note` の2段階呼び出し
（decisions/0004）の出力を観察した。

## 結果概要

7件すべてで以下の両方が成功した（decisions/0005 の検証観点）。

1. 設計されたスキーマ自体が妥当な JSON Schema だった（`Draft202012Validator.check_schema` 通過）
2. 抽出されたデータが、その（LLM自身が設計した）スキーマに従っていた（`jsonschema.validate` 通過）

## メモの種類ごとの設計傾向

- **`shopping_list.txt`**: 単純な文字列配列（`items: [string]`）になると
  想定していたが、実際は `items: [{name, quantity?, note?}]` という
  オブジェクト配列に設計された。「洗剤」のように数量指定のない品目は
  `quantity` を省略するなど、必須項目を `name` のみにする適切な設計だった
- **`meeting_notes.txt`**: `participants`（配列）・`decisions`（配列）・
  `action_items`（`{assignee, task, due_date}` のオブジェクト配列）
  ・`next_meeting` という、人間が設計してもおかしくない粒度の構造になった
- **`todo_scrawl.txt`**: 各タスクを `{content, context?, timing?}` に分解。
  「本返す 図書館」を `content: "本返す"` / `context: "図書館"` に、
  「今週中」「暇なとき」のような曖昧な期限を `timing` にまとめるなど、
  自由記述のノイズを適切に構造へ分離していた
- **`travel_plan.txt`**: 日毎の予定を `daily_itineraries` の配列にしつつ、
  宿泊情報は `accommodation`（`is_booked: false` を含む）という
  別オブジェクトに分離した。「そろそろ取らないと」という一言から
  `is_booked: false` を推論できていた
- **`mixed_note.txt`**（日記とTODOの複合メモ、あえて曖昧にした題材）:
  想定していたほどの混乱は見られず、`reflection`（振り返り）と
  `todos`（配列）の2フィールドにきれいに分離された。曖昧な題材でも
  「日記的な内容」と「タスク的な内容」という2軸に自己整理する傾向が見えた

## 解釈

7件全てでスキーマ設計・データ抽出・検証が一貫して成功しており、
Step1-A2（固定スキーマ）で見られたような「LLM が独自の解釈で規則から
逸脱する」というブレは、今回はスキーマ設計・データ抽出の両方を
同じ LLM に任せているため観測されなかった（そもそも LLM 自身が
設計した基準に対して LLM 自身がデータを埋めるため、整合性が取りやすい）。

今回はレート制限（429）を避けるため逐次実行・リトライで対応した。
実行頻度が増える場合は待機時間の調整が必要になる可能性がある。
