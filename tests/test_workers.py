import json
from unittest.mock import AsyncMock, call, patch

import pytest

from src.utils.exceptions import WorkerError
from src.workers import PlanResponse, SAAsWorkers, WorkerTask


@pytest.fixture
def mock_assistant():
    return AsyncMock()


@pytest.fixture
def workers():
    return SAAsWorkers(num_workers=3)


@pytest.mark.asyncio
async def test_plan_tasks_single_task(workers, mock_assistant):
    expected_response = PlanResponse(
        objective_completion=True,
        explanation="This is a simple task that doesn't require subtasks.",
        tasks=None,
    )
    json_response = json.dumps(expected_response.model_dump())

    def check_plan(assistant, prompt):
        assert "Simple objective" in prompt
        return json_response

    with patch("src.workers.Assistant") as MockAssistant:
        MockAssistant.return_value = AsyncMock()
        with patch("src.workers.get_full_response", side_effect=check_plan):
            result = await workers.plan_tasks("Simple objective", mock_assistant)

    assert isinstance(result, PlanResponse)
    assert result.objective_completion == True
    assert result.explanation == "This is a simple task that doesn't require subtasks."
    assert result.tasks is None
    MockAssistant.assert_called_once_with(
        name="TaskPlanner",
        llm=mock_assistant.llm,
        description="You are a task planner that analyzes objectives and breaks them down into subtasks if necessary.",
    )


@pytest.mark.asyncio
async def test_plan_tasks_multiple_tasks(workers, mock_assistant):
    expected_response = PlanResponse(
        objective_completion=False,
        explanation="This objective requires multiple subtasks.",
        tasks=[
            WorkerTask(task="Subtask 1", prompt="Do subtask 1"),
            WorkerTask(task="Subtask 2", prompt="Do subtask 2"),
            WorkerTask(task="Subtask 3", prompt="Do subtask 3"),
        ],
    )
    json_response = json.dumps(expected_response.model_dump())

    def check_plan(assistant, prompt):
        assert "Complex objective" in prompt
        return json_response

    with patch("src.workers.Assistant") as MockAssistant:
        MockAssistant.return_value = AsyncMock()
        with patch("src.workers.get_full_response", side_effect=check_plan):
            result = await workers.plan_tasks("Complex objective", mock_assistant)

    assert isinstance(result, PlanResponse)
    assert result.objective_completion == False
    assert result.explanation == "This objective requires multiple subtasks."
    assert len(result.tasks) == 3
    assert all(isinstance(task, WorkerTask) for task in result.tasks)
    MockAssistant.assert_called_once_with(
        name="TaskPlanner",
        llm=mock_assistant.llm,
        description="You are a task planner that analyzes objectives and breaks them down into subtasks if necessary.",
    )


@pytest.mark.asyncio
async def test_process_tasks(workers):
    tasks = [
        WorkerTask(task="Task 1", prompt="Do task 1"),
        WorkerTask(task="Task 2", prompt="Do task 2"),
        WorkerTask(task="Task 3", prompt="Do task 3"),
    ]
    workers.execute_task = AsyncMock(side_effect=["Result 1", "Result 2", "Result 3"])
    results = await workers.process_tasks(tasks)
    assert len(results) == 3
    assert all(task.result for task in results)
    assert [task.result for task in results] == ["Result 1", "Result 2", "Result 3"]


@pytest.mark.asyncio
async def test_execute_task(workers):
    worker = AsyncMock()
    task = WorkerTask(task="Test task", prompt="Test prompt")

    def check_execute(assistant, prompt):
        assert assistant == worker
        assert prompt == "Test prompt"
        return "Task result"

    with patch("src.workers.get_full_response", side_effect=check_execute):
        result = await workers.execute_task(worker, task)
    assert result == "Task result"


@pytest.mark.asyncio
async def test_summarize_results(workers, mock_assistant):
    objective = "Test objective"
    tasks = [
        WorkerTask(task="Task 1", prompt="Prompt 1", result="Result 1"),
        WorkerTask(task="Task 2", prompt="Prompt 2", result="Result 2"),
    ]
    expected_summary = "Summary of results"

    def check_prompt(assistant, prompt):
        assert assistant == mock_assistant
        assert objective in prompt
        assert all(task.task in prompt for task in tasks)
        assert all(task.result in prompt for task in tasks)
        return expected_summary

    with patch("src.workers.get_full_response", side_effect=check_prompt) as mock_get_full_response:
        result = await workers.summarize_results(objective, tasks, mock_assistant)

    assert result == expected_summary
    mock_get_full_response.assert_called_once()


@pytest.mark.asyncio
async def test_plan_tasks_error_handling(workers, mock_assistant):
    with patch("src.workers.Assistant"):
        with patch("src.workers.get_full_response", return_value="Invalid JSON"):
            with pytest.raises(WorkerError):
                await workers.plan_tasks("Test objective", mock_assistant)


@pytest.mark.asyncio
async def test_process_tasks_error_handling(workers):
    tasks = [WorkerTask(task="Task 1", prompt="Prompt 1")]
    workers.execute_task = AsyncMock(side_effect=Exception("Task execution error"))

    results = await workers.process_tasks(tasks)
    assert len(results) == 1
    assert results[0].result.startswith("Error:")


@pytest.mark.asyncio
async def test_execute_task_error_handling(workers):
    worker = AsyncMock()
    task = WorkerTask(task="Test task", prompt="Test prompt")

    with patch("src.workers.get_full_response", side_effect=Exception("Execution error")):
        with pytest.raises(WorkerError):
            await workers.execute_task(worker, task)
