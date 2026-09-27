"""指定フォルダ内のメモファイルの一覧・本文を取得するモジュール。"""

from pathlib import Path


def list_files(folder: str | Path) -> list[str]:
    """指定フォルダ直下にあるファイルの名前一覧を取得する。

    サブディレクトリは再帰的に探索せず、ディレクトリ自体は結果に含めない。

    Args:
        folder: 走査対象のフォルダパス。

    Returns:
        ファイル名を昇順にソートしたリスト。
    """
    folder_path = Path(folder)
    return sorted(p.name for p in folder_path.iterdir() if p.is_file())


def read_note(path: str | Path) -> str:
    """指定したメモファイル1件分の本文を読み込む。

    Args:
        path: 対象メモファイルのパス。

    Returns:
        メモの本文（UTF-8 テキスト）。
    """
    return Path(path).read_text(encoding="utf-8")
