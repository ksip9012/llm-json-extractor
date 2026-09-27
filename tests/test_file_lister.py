from pathlib import Path

from llm_json_extractor.file_lister import list_files, read_note

FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "sample_notes"
)


def test_list_files_returns_all_file_names():
    result = list_files(FIXTURES_DIR)

    assert len(result) == 7
    assert "shopping_list.txt" in result


def test_list_files_returns_sorted_names():
    result = list_files(FIXTURES_DIR)

    assert result == sorted(result)


def test_read_note_returns_file_contents():
    content = read_note(FIXTURES_DIR / "shopping_list.txt")

    assert "牛乳" in content
