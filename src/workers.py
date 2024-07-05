import asyncio
import json
from typing import List, Optional

from phi.assistant import Assistant
from pydantic import BaseModel, Field

from src.assistants import create_assistant, get_full_response
from src.config import settings
from src.utils.exceptions import WorkerError
from src.utils.logging import setup_logging

logger = setup_logging()


class WorkerTask(BaseModel):
    task: str = Field(..., description="Brief description of the task")
    prompt: str = Field(..., description="Detailed prompt for the worker to accomplish the task")
    result: Optional[str] = Field(None, description="Result of the task execution")


class PlanResponse(BaseModel):
    objective_completion: bool = Field(
        ..., description="Whether the objective can be completed without subtasks"
    )
    explanation: str = Field(
        ..., description="Explanation or direct response if objective_completion is True"
    )
    tasks: Optional[List[WorkerTask]] = Field(
        None, description="List of tasks if objective_completion is False"
    )


class SAAsWorkers:
    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.workers = [
            create_assistant(f"Worker{i}", settings.SUB_ASSISTANT) for i in range(num_workers)
        ]

    async def execute_task(self, worker: Assistant, task: WorkerTask) -> str:
        try:
            return await asyncio.to_thread(get_full_response, worker, task.prompt)
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            raise WorkerError(f"Error executing task: {str(e)}")

    async def process_tasks(self, tasks: List[WorkerTask]) -> List[WorkerTask]:
        worker_tasks = []
        for task, worker in zip(tasks, self.workers):
            worker_tasks.append(self.execute_task(worker, task))

        results = await asyncio.gather(*worker_tasks, return_exceptions=True)

        processed_tasks = []
        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Task failed: {task.task}. Error: {str(result)}")
                task.result = f"Error: {str(result)}"
            else:
                task.result = result
            processed_tasks.append(task)

        return processed_tasks

    @staticmethod
    async def plan_tasks(objective: str, main_assistant: Assistant) -> PlanResponse:
        plan_prompt = f"""
        Analyze the following objective and determine if it requires subtask decomposition:

        Objective: {objective}

        Respond with a JSON object that follows this structure:

        {{
            "objective_completion": boolean,
            "explanation": string,
            "tasks": [
                {{
                    "task": string,
                    "prompt": string
                }},
                ...
            ]
        }}

        If the objective can be accomplished without subtask decomposition:
        - Set "objective_completion" to true
        - Provide a concise solution or response to the objective in the "explanation" field
        - Leave the "tasks" array empty

        If the objective requires subtask decomposition:
        - Set "objective_completion" to false
        - Provide a brief explanation in the "explanation" field
        - Break down the objective into {settings.NUM_WORKERS} subtasks in the "tasks" array
        - For each subtask, include a "task" field with a brief description and a "prompt" field with detailed instructions

        Remember, you are a skilled prompt engineer. Create prompts that are clear, specific, and actionable.
        """

        planner = Assistant(
            name="TaskPlanner",
            llm=main_assistant.llm,
            description="You are a task planner that analyzes objectives and breaks them down into subtasks if necessary.",
        )

        response = await asyncio.to_thread(get_full_response, planner, plan_prompt)

        try:
            plan_dict = json.loads(response)
            return PlanResponse(**plan_dict)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            raise WorkerError("Failed to parse plan response as JSON")
        except ValueError as e:
            logger.error(f"Invalid plan response structure: {str(e)}")
            raise WorkerError(f"Invalid plan response structure: {str(e)}")

    @staticmethod
    async def summarize_results(
        objective: str, results: List[WorkerTask], refiner_assistant: Assistant
    ) -> str:
        summary_prompt = f"Objective: {objective}\n\nTask results:\n"
        for task in results:
            summary_prompt += f"Task: {task.task}\nResult: {task.result}\n\n"
        summary_prompt += "Please summarize these results into a coherent final output that addresses the original objective."

        return await asyncio.to_thread(get_full_response, refiner_assistant, summary_prompt)
