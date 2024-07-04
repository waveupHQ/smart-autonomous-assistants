import json
import os
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from .assistants import create_assistant, get_full_response
from .config import settings
from .utils.exceptions import WorkflowError, AssistantError
from .utils.logging import setup_logging

logger = setup_logging()


class TaskExchange(BaseModel):
    role: Literal["user", "main_assistant", "sub_assistant", "refiner_assistant"] = Field(...)
    content: str = Field(...)


class Task(BaseModel):
    task: str
    result: str

    def to_dict(self) -> Dict[str, Any]:
        return {"task": str(self.task), "result": str(self.result)}


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

    def __init__(self, **data):
        super().__init__(**data)
        os.makedirs(self.output_dir, exist_ok=True)

    def run_workflow(self, objective: str) -> str:
        """
        Executes the workflow to accomplish the given objective.

        Args:
            objective (str): The main task or goal to be accomplished.

        Returns:
            str: The final refined output of the workflow.
        """

        logger.info(f"Starting workflow with objective: {objective}")
        self.state.task_exchanges.append(TaskExchange(role="user", content=objective))
        task_counter = 1
        try:
            while True:
                logger.info(f"Starting task {task_counter}")
                main_prompt = self._generate_main_prompt(objective)
                main_response = self._get_assistant_response("main", main_prompt)

                if main_response.startswith("ALL DONE:"):
                    logger.info("Workflow completed")
                    break

                sub_task_prompt = self._generate_sub_task_prompt(main_response)
                sub_response = self._get_assistant_response("sub", sub_task_prompt)

                self.state.tasks.append(Task(task=main_response, result=sub_response))
                task_counter += 1

            refined_output = self._get_refined_output(objective)
            self._save_exchange_log(objective, refined_output)
            logger.info("Exchange log saved")

            return refined_output
        except AssistantError as e:
            logger.error(f"Assistant error: {str(e)}")
            raise WorkflowError(f"Workflow failed due to assistant error: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error in workflow execution")
            raise WorkflowError(f"Unexpected error in workflow execution: {str(e)}")

    def _generate_main_prompt(self, objective: str) -> str:
        return (
            f"Objective: {objective}\n\n"
            f"Current progress:\n{json.dumps(self.state.to_dict(), indent=2)}\n\n"
            "Break down this objective into the next specific sub-task, or if the objective is fully achieved, "
            "start your response with 'ALL DONE:' followed by the final output."
        )

    def _generate_sub_task_prompt(self, main_response: str) -> str:
        return (
            f"Previous tasks: {json.dumps([task.to_dict() for task in self.state.tasks], indent=2)}\n\n"
            f"Current task: {main_response}\n\n"
            "Execute this task and provide the result. Use the provided functions to create, read, or list files as needed. "
            f"All file operations should be relative to the '{self.output_dir}' directory."
        )

    def _get_assistant_response(self, assistant_type: str, prompt: str) -> str:
        try:
            assistant_model = getattr(settings, f"{assistant_type.upper()}_ASSISTANT")
            assistant = create_assistant(f"{assistant_type.capitalize()}Assistant", assistant_model)
            response = get_full_response(assistant, prompt)
            logger.info(f"{assistant_type.capitalize()} assistant response received")
            self.state.task_exchanges.append(
                TaskExchange(role=f"{assistant_type}_assistant", content=response)
            )
            return response
        except Exception as e:
            logger.error(f"Error getting response from {assistant_type} assistant: {str(e)}")
            raise AssistantError(
                f"Error getting response from {assistant_type} assistant: {str(e)}"
            )

    def _get_refined_output(self, objective: str) -> str:
        refiner_prompt = (
            f"Original objective: {objective}\n\n"
            f"Task breakdown and results: {json.dumps([task.to_dict() for task in self.state.tasks], indent=2)}\n\n"
            "Please refine these results into a coherent final output, summarizing the project structure created. "
            f"You can use the provided functions to list and read files if needed. All files are in the '{self.output_dir}' directory. "
            "Provide your response as a string, not a list or dictionary."
        )
        return self._get_assistant_response("refiner", refiner_prompt)

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
