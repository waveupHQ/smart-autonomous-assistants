from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


@pytest.fixture
def mock_orchestrator():
    with patch("src.main.Orchestrator") as MockOrchestrator:
        mock_instance = MagicMock()
        mock_instance.run_workflow = AsyncMock(return_value="Mocked workflow result")
        MockOrchestrator.return_value = mock_instance
        yield MockOrchestrator


@pytest.fixture
def mock_asyncio_run():
    with patch("src.main.asyncio.run", new_callable=MagicMock) as mock_run:
        mock_run.return_value = "Mocked workflow result"
        yield mock_run


def print_call_args(mock_call):
    print(f"Call args: {mock_call.call_args}")
    print(f"Call args list: {mock_call.call_args.args if mock_call.call_args else 'No args'}")
    print(f"Call kwargs: {mock_call.call_args.kwargs if mock_call.call_args else 'No kwargs'}")


def test_run_workflow_with_custom_prompt(mock_orchestrator, mock_asyncio_run):
    custom_prompt = "This is a {objective} custom prompt template"
    result = runner.invoke(
        app, ["run-workflow", "Test objective", "--custom-prompt", custom_prompt]
    )

    assert result.exit_code == 0
    assert "Using custom prompt template" in result.stdout

    mock_orchestrator.assert_called_once()
    print_call_args(mock_orchestrator)

    mock_orchestrator.return_value.run_workflow.assert_called_once()
    print_call_args(mock_orchestrator.return_value.run_workflow)

    call_args = mock_orchestrator.return_value.run_workflow.call_args
    assert call_args is not None, "run_workflow was not called"
    if call_args.args:
        assert "Test objective" in call_args.args[0]
    elif call_args.kwargs:
        assert "Test objective" in call_args.kwargs.get("objective", "")


def test_run_workflow_without_custom_prompt(mock_orchestrator, mock_asyncio_run):
    result = runner.invoke(app, ["run-workflow", "Test objective"])

    assert result.exit_code == 0
    assert "Using custom prompt template" not in result.stdout

    mock_orchestrator.assert_called_once()
    print_call_args(mock_orchestrator)

    mock_orchestrator.return_value.run_workflow.assert_called_once()
    print_call_args(mock_orchestrator.return_value.run_workflow)

    call_args = mock_orchestrator.return_value.run_workflow.call_args
    assert call_args is not None, "run_workflow was not called"
    if call_args.args:
        assert "Test objective" in call_args.args[0]
    elif call_args.kwargs:
        assert "Test objective" in call_args.kwargs.get("objective", "")


def test_run_workflow_with_plugin(mock_orchestrator, mock_asyncio_run):
    result = runner.invoke(app, ["run-workflow", "Test objective", "--plugin", "test_plugin"])

    assert result.exit_code == 0
    assert "Using plugin: test_plugin" in result.stdout

    mock_orchestrator.return_value.run_workflow.assert_called_once()
    print_call_args(mock_orchestrator.return_value.run_workflow)

    call_args = mock_orchestrator.return_value.run_workflow.call_args
    assert call_args is not None, "run_workflow was not called"
    if call_args.args:
        assert "Test objective" in call_args.args[0]
        assert call_args.args[1] == "test_plugin" if len(call_args.args) > 1 else True
    elif call_args.kwargs:
        assert "Test objective" in call_args.kwargs.get("objective", "")
        assert call_args.kwargs.get("use_case") == "test_plugin"
