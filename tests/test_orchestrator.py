import os
from unittest.mock import AsyncMock, patch

import pytest

from src.orchestrator import Orchestrator, Task, TaskExchange
from src.plugin_manager import PluginSpec
from src.utils.exceptions import WorkflowError
from src.workers import PlanResponse, WorkerTask


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
    task = Task(task="Test task", prompt="Test prompt", result="Test result")
    assert task.task == "Test task"
    assert task.result == "Test result"
    assert task.to_dict() == {"task": "Test task", "prompt": "Test prompt", "result": "Test result"}


@pytest.mark.asyncio
@patch("src.orchestrator.create_assistant")
async def test_run_workflow_single_task(mock_create_assistant, orchestrator):
    mock_main_assistant = AsyncMock()
    mock_refiner_assistant = AsyncMock()
    mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

    mock_plan_response = PlanResponse(
        objective_completion=True, explanation="This is a simple task.", tasks=None
    )
    orchestrator.workers.plan_tasks = AsyncMock(return_value=mock_plan_response)

    result = await orchestrator.run_workflow("Test objective")

    assert result == "This is a simple task."
    assert len(orchestrator.state.task_exchanges) == 2
    assert orchestrator.state.task_exchanges[0].role == "user"
    assert orchestrator.state.task_exchanges[1].role == "main_assistant"


@pytest.mark.asyncio
@patch("src.orchestrator.create_assistant")
async def test_run_workflow_multiple_tasks(mock_create_assistant, orchestrator):
    mock_main_assistant = AsyncMock()
    mock_refiner_assistant = AsyncMock()
    mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

    mock_plan_response = PlanResponse(
        objective_completion=False,
        explanation="This task requires multiple steps.",
        tasks=[
            WorkerTask(task="Subtask 1", prompt="Do subtask 1"),
            WorkerTask(task="Subtask 2", prompt="Do subtask 2"),
        ],
    )
    orchestrator.workers.plan_tasks = AsyncMock(return_value=mock_plan_response)
    orchestrator.workers.process_tasks = AsyncMock(
        return_value=[
            WorkerTask(task="Subtask 1", prompt="Do subtask 1", result="Result 1"),
            WorkerTask(task="Subtask 2", prompt="Do subtask 2", result="Result 2"),
        ]
    )
    orchestrator.workers.summarize_results = AsyncMock(return_value="Final summary")

    result = await orchestrator.run_workflow("Test objective")

    assert result == "Final summary"
    assert len(orchestrator.state.task_exchanges) == 5
    assert orchestrator.state.task_exchanges[0].role == "user"
    assert orchestrator.state.task_exchanges[1].role == "main_assistant"
    assert orchestrator.state.task_exchanges[2].role == "sub_assistant"
    assert orchestrator.state.task_exchanges[3].role == "sub_assistant"
    assert orchestrator.state.task_exchanges[4].role == "refiner_assistant"


@pytest.mark.asyncio
@patch("src.orchestrator.create_assistant")
async def test_run_workflow_error(mock_create_assistant, orchestrator):
    mock_main_assistant = AsyncMock()
    mock_create_assistant.return_value = mock_main_assistant

    orchestrator.workers.plan_tasks = AsyncMock(side_effect=Exception("API Error"))

    with pytest.raises(WorkflowError):
        await orchestrator.run_workflow("Test objective")


def test_save_exchange_log(orchestrator):
    orchestrator.state.task_exchanges = [
        TaskExchange(role="user", content="Test objective"),
        TaskExchange(role="main_assistant", content="Test response"),
    ]

    orchestrator._save_exchange_log("Test objective", "Test output")

    log_file_path = os.path.join(orchestrator.output_dir, "exchange_log.md")
    assert os.path.exists(log_file_path)

    with open(log_file_path, "r") as f:
        content = f.read()
        assert "Test objective" in content
        assert "Test response" in content
        assert "Test output" in content


def test_state_to_dict(orchestrator):
    orchestrator.state.task_exchanges.append(TaskExchange(role="user", content="Test"))
    orchestrator.state.tasks.append(
        Task(task="Test task", prompt="Test prompt", result="Test result")
    )

    state_dict = orchestrator.state.to_dict()
    assert len(state_dict["task_exchanges"]) == 1
    assert len(state_dict["tasks"]) == 1


@pytest.mark.asyncio
async def test_run_workflow_with_plugin(orchestrator):
    class TestPlugin(PluginSpec):
        def get_use_case_prompt(self, objective: str) -> str:
            return f"Test plugin prompt for: {objective}"

    orchestrator.use_case_prompts = {"TestPlugin": TestPlugin().get_use_case_prompt}

    with patch("src.orchestrator.create_assistant") as mock_create_assistant, patch(
        "src.workers.SAAsWorkers.plan_tasks"
    ) as mock_plan_tasks:

        mock_main_assistant = AsyncMock()
        mock_refiner_assistant = AsyncMock()
        mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

        mock_plan_tasks.return_value = PlanResponse(
            objective_completion=True, explanation="Test result"
        )

        result = await orchestrator.run_workflow("Test objective", use_case="TestPlugin")

        assert result == "Test result"
        mock_plan_tasks.assert_called_once()
        assert "Test plugin prompt for: Test objective" in mock_plan_tasks.call_args[0][0]


@pytest.mark.asyncio
async def test_run_workflow_with_custom_prompt(orchestrator):
    custom_prompt = "Custom prompt: {objective}"
    orchestrator.settings.custom_prompt_template = custom_prompt

    with patch("src.orchestrator.create_assistant") as mock_create_assistant, patch(
        "src.workers.SAAsWorkers.plan_tasks"
    ) as mock_plan_tasks:

        mock_main_assistant = AsyncMock()
        mock_refiner_assistant = AsyncMock()
        mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

        mock_plan_tasks.return_value = PlanResponse(
            objective_completion=True, explanation="Test result"
        )

        result = await orchestrator.run_workflow("Test objective")

        assert result == "Test result"
        mock_plan_tasks.assert_called_once()
        assert "Custom prompt: Test objective" in mock_plan_tasks.call_args[0][0]


@pytest.mark.asyncio
async def test_run_workflow_plugin_not_found(orchestrator):
    with pytest.raises(WorkflowError) as exc_info:
        await orchestrator.run_workflow("Test objective", use_case="NonExistentPlugin")
    assert "Plugin 'NonExistentPlugin' not found" in str(exc_info.value)
