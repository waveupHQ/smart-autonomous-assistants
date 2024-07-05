import os
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field

from .assistants import create_assistant
from .config import settings
from .utils.exceptions import AssistantError, WorkflowError
from .utils.logging import setup_logging
from .workers import PlanResponse, SAAsWorkers

logger = setup_logging()


class TaskExchange(BaseModel):
    role: Literal["user", "main_assistant", "sub_assistant", "refiner_assistant"] = Field(...)
    content: str = Field(...)


class Task(BaseModel):
    task: str
    prompt: str
    result: str

    def to_dict(self) -> Dict[str, Any]:
        return {"task": str(self.task), "prompt": str(self.prompt), "result": str(self.result)}


class State(BaseModel):
    task_exchanges: List[TaskExchange] = []
    tasks: List[Task] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_exchanges": [exchange.model_dump() for exchange in self.task_exchanges],
            "tasks": [task.to_dict() for task in self.tasks],
        }


class Orchestrator(BaseModel):
    state: State = State()
    output_dir: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "output"))
    workers: SAAsWorkers = Field(default_factory=lambda: SAAsWorkers(settings.NUM_WORKERS))

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        os.makedirs(self.output_dir, exist_ok=True)

    async def run_workflow(self, objective: str) -> str:
        """
        Executes the workflow to accomplish the given objective using SAAsWorkers.

        Args:
            objective (str): The main task or goal to be accomplished.

        Returns:
            str: The final refined output of the workflow.
        """
        logger.info(f"Starting workflow with objective: {objective}")
        self.state.task_exchanges.append(TaskExchange(role="user", content=objective))

        try:
            main_assistant = create_assistant("MainAssistant", settings.MAIN_ASSISTANT)
            refiner_assistant = create_assistant("RefinerAssistant", settings.REFINER_ASSISTANT)

            # Plan tasks
            plan_result: PlanResponse = await self.workers.plan_tasks(objective, main_assistant)

            if plan_result.objective_completion:
                # Single-task scenario
                final_output = plan_result.explanation
                self.state.task_exchanges.append(
                    TaskExchange(role="main_assistant", content=final_output)
                )
            else:
                # Multi-task scenario
                tasks = plan_result.tasks if plan_result.tasks else []
                self.state.task_exchanges.append(
                    TaskExchange(role="main_assistant", content="\n".join([t.task for t in tasks]))
                )

                # Process tasks
                results = await self.workers.process_tasks(tasks)
                for result in results:
                    self.state.tasks.append(
                        Task(task=result.task, prompt=result.prompt, result=result.result)
                    )
                    self.state.task_exchanges.append(
                        TaskExchange(role="sub_assistant", content=result.result)
                    )

                # Summarize results
                final_output = await self.workers.summarize_results(
                    objective, results, refiner_assistant
                )
                self.state.task_exchanges.append(
                    TaskExchange(role="refiner_assistant", content=final_output)
                )

            self._save_exchange_log(objective, final_output)
            logger.info("Workflow completed and exchange log saved")

            return final_output

        except AssistantError as e:
            logger.error(f"Assistant error: {str(e)}")
            raise WorkflowError(f"Workflow failed due to assistant error: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in workflow execution")
            raise WorkflowError(f"Unexpected error in workflow execution: {str(e)}")

    def _save_exchange_log(self, objective: str, final_output: str):
        """
        Saves the workflow exchange log to a markdown file.

        Args:
            objective (str): The original objective of the workflow.
            final_output (str): The final refined output of the workflow.
        """
        log_content = "# SAA Orchestrator Exchange Log\n\n"
        log_content += f"## Objective\n{objective}\n\n"
        log_content += "## Task Breakdown and Execution\n\n"

        for exchange in self.state.task_exchanges:
            log_content += f"### {exchange.role.capitalize()}\n{exchange.content}\n\n"

        log_content += f"## Final Output\n{final_output}\n"

        log_file_path = os.path.join(self.output_dir, "exchange_log.md")
        with open(log_file_path, "w") as f:
            f.write(log_content)
        logger.info(f"Exchange log saved to: {log_file_path}")
