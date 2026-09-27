# fixtures

実装・テスト・README での例示に使うダミーデータ置き場。実在の人物・予定・
個人メモは使わない（[decisions/0002](../decisions/0002-use-diverse-personal-memos-as-input.md) 参照）。

- `sample_notes/`: 種類の異なる短い自由入力メモ（1ファイル = 1メモ）。
  メモの種類によって自然な JSON 構造が異なるように、あえて多様な形式を
  用意している。
  - `shopping_list.txt`: 買い物リスト（単純な配列になりやすい）
  - `meeting_notes.txt`: 会議メモ（参加者・決定事項・アクションアイテムのような入れ子構造）
  - `diary_entry.txt`: 日記（日付・気分・出来事のような主観的な項目）
  - `todo_scrawl.txt`: TODO の走り書き（優先度の有無が曖昧）
  - `book_review.txt`: 読書感想（タイトル・評価・感想のような評価軸のある構造）
  - `travel_plan.txt`: 旅行の予定メモ（日時・場所が絡む複雑な構造）
  - `mixed_note.txt`: 日記と TODO が混在した曖昧な複合メモ（あえて一意に決まらないケース）
