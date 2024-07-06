from unittest.mock import PropertyMock, patch

import pytest


@pytest.fixture
def mock_settings():
    with patch("src.config.Settings") as MockSettings:
        mock_instance = MockSettings.return_value
        mock_instance.PROJECT_NAME = "SAA-Orchestrator"
        mock_instance.PROJECT_ID = "test_project"
        mock_instance.LOCATION = "test_location"
        mock_instance.ANTHROPIC_API_KEY = "test_anthropic_key"
        mock_instance.OPENAI_API_KEY = "test_openai_key"
        mock_instance.TAVILY_API_KEY = "test_tavily_key"
        mock_instance.NUM_WORKERS = 3
        mock_instance.MAIN_ASSISTANT = "claude-3-sonnet-20240229"
        mock_instance.SUB_ASSISTANT = "claude-3-haiku-20240307"
        mock_instance.REFINER_ASSISTANT = "gemini-1.5-pro-preview-0409"

        # Mock property methods
        type(mock_instance).anthropic_api_key = PropertyMock(return_value="test_anthropic_key")
        type(mock_instance).openai_api_key = PropertyMock(return_value="test_openai_key")
        type(mock_instance).tavily_api_key = PropertyMock(return_value="test_tavily_key")

        yield mock_instance


def test_settings_initialization(mock_settings):
    assert mock_settings.PROJECT_NAME == "SAA-Orchestrator"
    assert mock_settings.PROJECT_ID == "test_project"
    assert mock_settings.LOCATION == "test_location"
    assert mock_settings.ANTHROPIC_API_KEY == "test_anthropic_key"
    assert mock_settings.OPENAI_API_KEY == "test_openai_key"
    assert mock_settings.TAVILY_API_KEY == "test_tavily_key"


def test_api_key_properties(mock_settings):
    assert mock_settings.anthropic_api_key == "test_anthropic_key"
    assert mock_settings.openai_api_key == "test_openai_key"
    assert mock_settings.tavily_api_key == "test_tavily_key"


def test_missing_api_keys():
    with patch("src.config.Settings") as MockSettings:
        mock_instance = MockSettings.return_value

        # Mock property methods to raise ValueError
        type(mock_instance).anthropic_api_key = PropertyMock(
            side_effect=ValueError("ANTHROPIC_API_KEY is not set in the environment")
        )
        type(mock_instance).openai_api_key = PropertyMock(
            side_effect=ValueError("OPENAI_API_KEY is not set in the environment")
        )
        type(mock_instance).tavily_api_key = PropertyMock(
            side_effect=ValueError("TAVILY_API_KEY is not set in the environment")
        )

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is not set in the environment"):
            _ = mock_instance.anthropic_api_key

        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set in the environment"):
            _ = mock_instance.openai_api_key

        with pytest.raises(ValueError, match="TAVILY_API_KEY is not set in the environment"):
            _ = mock_instance.tavily_api_key


def test_default_values(mock_settings):
    assert mock_settings.NUM_WORKERS == 3
    assert mock_settings.MAIN_ASSISTANT == "claude-3-sonnet-20240229"
    assert mock_settings.SUB_ASSISTANT == "claude-3-haiku-20240307"
    assert mock_settings.REFINER_ASSISTANT == "gemini-1.5-pro-preview-0409"
