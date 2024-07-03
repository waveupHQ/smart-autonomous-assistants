import json
import logging
import os
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field
from rich import print as rprint

from .assistants import create_assistant, get_full_response
from .config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
    """
    Manages the workflow of AI assistants to accomplish complex tasks.
    """

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
        rprint(f"[bold green]Starting workflow with objective:[/bold green] {objective}")
        logging.info(f"Starting workflow with objective: {objective}")
        self.state.task_exchanges.append(TaskExchange(role="user", content=objective))

        task_counter = 1
        while True:
            rprint(f"\n[bold blue]--- Task {task_counter} ---[/bold blue]")
            logging.info(f"Starting task {task_counter}")
            main_prompt = (
                f"Objective: {objective}\n\n"
                f"Current progress:\n{json.dumps(self.state.to_dict(), indent=2)}\n\n"
                "Break down this objective into the next specific sub-task, or if the objective is fully achieved, "
                "start your response with 'ALL DONE:' followed by the final output."
            )
            logging.debug(f"Main prompt: {main_prompt}")
            main_response = get_full_response(
                create_assistant("MainAssistant", settings.MAIN_ASSISTANT), main_prompt
            )

            logging.info("Main assistant response received")
            self.state.task_exchanges.append(
                TaskExchange(role="main_assistant", content=main_response)
            )
            rprint(f"[green]MAIN_ASSISTANT response:[/green] {main_response[:100]}...")

            if main_response.startswith("ALL DONE:"):
                rprint("[bold green]Workflow completed![/bold green]")
                logging.info("Workflow completed")
                break

            sub_task_prompt = (
                f"Previous tasks: {json.dumps([task.to_dict() for task in self.state.tasks], indent=2)}\n\n"
                f"Current task: {main_response}\n\n"
                "Execute this task and provide the result. Use the provided functions to create, read, or list files as needed. "
                f"All file operations should be relative to the '{self.output_dir}' directory."
            )
            logging.debug(f"Sub-task prompt: {sub_task_prompt}")
            sub_response = get_full_response(
                create_assistant("SubAssistant", settings.SUB_ASSISTANT), sub_task_prompt
            )

            logging.info("Sub-assistant response received")
            self.state.task_exchanges.append(
                TaskExchange(role="sub_assistant", content=sub_response)
            )
            self.state.tasks.append(Task(task=main_response, result=sub_response))
            rprint(f"[green]SUB_ASSISTANT response:[/green] {sub_response[:100]}...")

            task_counter += 1

        refiner_prompt = (
            f"Original objective: {objective}\n\n"
            f"Task breakdown and results: {json.dumps([task.to_dict() for task in self.state.tasks], indent=2)}\n\n"
            "Please refine these results into a coherent final output, summarizing the project structure created. "
            f"You can use the provided functions to list and read files if needed. All files are in the '{self.output_dir}' directory. "
            "Provide your response as a string, not a list or dictionary."
        )
        logging.debug(f"Refiner prompt: {refiner_prompt}")
        refined_output = get_full_response(
            create_assistant("RefinerAssistant", settings.REFINER_ASSISTANT), refiner_prompt
        )

        logging.info("Refiner assistant response received")
        self.state.task_exchanges.append(
            TaskExchange(role="refiner_assistant", content=refined_output)
        )
        rprint(f"[green]REFINER_ASSISTANT response:[/green] {refined_output[:100]}...")

        self._save_exchange_log(objective, refined_output)
        rprint("[bold blue]Exchange log saved to 'exchange_log.md'[/bold blue]")
        logging.info("Exchange log saved")

        return refined_output

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
        rprint(f"[blue]Exchange log saved to:[/blue] {log_file_path}")
