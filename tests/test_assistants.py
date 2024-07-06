from unittest.mock import MagicMock, patch

import pytest

from src.assistants import create_assistant, create_file, list_files, read_file
from src.utils.exceptions import AssistantError


@pytest.fixture
def mock_assistant():
    return MagicMock()


def test_create_file(tmp_path):
    test_dir = tmp_path / "output"
    test_dir.mkdir()
    with patch("src.assistants.output_dir", str(test_dir)):
        result = create_file("test.txt", "Hello, World!")
        assert result == f"File created: {test_dir}/test.txt"
        assert (test_dir / "test.txt").read_text() == "Hello, World!"


def test_read_file(tmp_path):
    test_dir = tmp_path / "output"
    test_dir.mkdir()
    test_file = test_dir / "test.txt"
    test_file.write_text("Hello, World!")
    with patch("src.assistants.output_dir", str(test_dir)):
        assert read_file("test.txt") == "Hello, World!"
        assert read_file("nonexistent.txt") == f"File not found: {test_dir}/nonexistent.txt"


def test_list_files(tmp_path):
    test_dir = tmp_path / "output"
    test_dir.mkdir()
    (test_dir / "file1.txt").touch()
    (test_dir / "file2.txt").touch()
    with patch("src.assistants.output_dir", str(test_dir)):
        files = list_files()
        assert "file1.txt" in files and "file2.txt" in files
        assert list_files("nonexistent") == f"Directory not found: {test_dir}/nonexistent"


@patch("src.assistants.Claude")
@patch("src.assistants.Gemini")
@patch("src.assistants.OpenAIChat")
@patch("src.assistants.Assistant")
def test_create_assistant(mock_assistant_class, mock_openai, mock_gemini, mock_claude):
    mock_assistant_instance = MagicMock()
    mock_assistant_class.return_value = mock_assistant_instance

    create_assistant("TestAssistant", "claude-3-opus-20240229")
    mock_claude.assert_called_once()
    mock_assistant_class.assert_called_once()

    create_assistant("TestAssistant", "gpt-4")
    mock_openai.assert_called_once()

    create_assistant("TestAssistant", "gemini-pro")
    mock_gemini.assert_called_once()

    with pytest.raises(
        AssistantError,
        match="Error creating assistant TestAssistant with model unsupported-model: Unsupported model: unsupported-model",
    ):
        create_assistant("TestAssistant", "unsupported-model")
