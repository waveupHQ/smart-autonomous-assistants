import os
from unittest.mock import MagicMock, patch

import pytest

from src.orchestrator import Orchestrator, Task, TaskExchange


@pytest.fixture
def orchestrator(tmp_path):
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return Orchestrator(output_dir=str(output_dir))


def test_orchestrator_initialization(orchestrator):
    assert orchestrator.state is not None
    assert len(orchestrator.state.task_exchanges) == 0
    assert len(orchestrator.state.tasks) == 0


def test_task_exchange():
    exchange = TaskExchange(role="user", content="Test content")
    assert exchange.role == "user"
    assert exchange.content == "Test content"


def test_task():
    task = Task(task="Test task", result="Test result")
    assert task.task == "Test task"
    assert task.result == "Test result"
    assert task.to_dict() == {"task": "Test task", "result": "Test result"}


@patch("src.orchestrator.create_assistant")
@patch("src.orchestrator.get_full_response")
def test_run_workflow(mock_get_full_response, mock_create_assistant, orchestrator):
    mock_assistant = MagicMock()
    mock_create_assistant.return_value = mock_assistant

    mock_get_full_response.side_effect = [
        "First sub-task",
        "Result of first sub-task",
        "ALL DONE: Final output",
        "Refined output",
    ]

    result = orchestrator.run_workflow("Test objective")

    assert isinstance(result, str), f"Expected string result, but got {type(result)}"
    assert "Refined output" in result, f"Expected 'Refined output' in result, but got: {result}"

    # Check the number of task exchanges
    assert (
        len(orchestrator.state.task_exchanges) == 5
    ), f"Expected 5 task exchanges, but got {len(orchestrator.state.task_exchanges)}"

    # Check the roles of task exchanges
    expected_roles = [
        "user",
        "main_assistant",
        "sub_assistant",
        "main_assistant",
        "refiner_assistant",
    ]
    actual_roles = [exchange.role for exchange in orchestrator.state.task_exchanges]
    assert (
        actual_roles == expected_roles
    ), f"Expected roles {expected_roles}, but got {actual_roles}"

    # Check the number of tasks
    assert (
        len(orchestrator.state.tasks) == 1
    ), f"Expected 1 task, but got {len(orchestrator.state.tasks)}"

    # Print task exchanges for debugging
    print("\nTask Exchanges:")
    for i, exchange in enumerate(orchestrator.state.task_exchanges):
        print(f"{i+1}. Role: {exchange.role}, Content: {exchange.content[:50]}...")

    # Check mock calls
    assert (
        mock_get_full_response.call_count == 4
    ), f"Expected 4 calls to get_full_response, but got {mock_get_full_response.call_count}"
    assert (
        mock_create_assistant.call_count == 4
    ), f"Expected 4 calls to create_assistant, but got {mock_create_assistant.call_count}"

    # Check if exchange log was created
    assert os.path.exists(
        os.path.join(orchestrator.output_dir, "exchange_log.md")
    ), "Exchange log file was not created"


@patch("builtins.open", new_callable=MagicMock)
@patch("os.path.join", return_value="mocked_path")
def test_save_exchange_log(mock_join, mock_open, orchestrator):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    orchestrator.state.task_exchanges = [
        TaskExchange(role="user", content="Test objective"),
        TaskExchange(role="main_assistant", content="Test response"),
    ]

    orchestrator._save_exchange_log("Test objective", "Test output")

    mock_open.assert_called_once_with("mocked_path", "w")
    mock_file.write.assert_called()


@patch("src.orchestrator.get_full_response")
def test_run_workflow_error(mock_get_full_response, orchestrator):
    mock_get_full_response.side_effect = Exception("API Error")

    with pytest.raises(Exception):
        orchestrator.run_workflow("Test objective")


def test_task_exchange_validation():
    with pytest.raises(ValueError):
        TaskExchange(role="invalid_role", content="Test content")


def test_state_to_dict(orchestrator):
    orchestrator.state.task_exchanges.append(TaskExchange(role="user", content="Test"))
    orchestrator.state.tasks.append(Task(task="Test task", result="Test result"))

    state_dict = orchestrator.state.to_dict()
    assert len(state_dict["task_exchanges"]) == 1
    assert len(state_dict["tasks"]) == 1
