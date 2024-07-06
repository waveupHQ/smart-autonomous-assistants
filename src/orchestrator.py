import os
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .assistants import create_assistant
from .config import settings
from .plugin_manager import plugin_manager
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


class OrchestratorSettings(BaseModel):
    main_assistant_model: str = settings.MAIN_ASSISTANT
    sub_assistant_model: str = settings.SUB_ASSISTANT
    refiner_assistant_model: str = settings.REFINER_ASSISTANT
    num_workers: int = settings.NUM_WORKERS
    additional_tools: Optional[List] = None
    custom_prompt_template: Optional[str] = None


class Orchestrator(BaseModel):
    state: State = State()
    output_dir: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "output"))
    workers: SAAsWorkers = Field(default_factory=lambda: SAAsWorkers(settings.NUM_WORKERS))
    settings: OrchestratorSettings = Field(default_factory=OrchestratorSettings)

    use_case_prompts: Dict[str, Callable] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        os.makedirs(self.output_dir, exist_ok=True)
        self.use_case_prompts = plugin_manager.get_use_case_prompts()

    async def run_workflow(self, objective: str, use_case: Optional[str] = None) -> str:
        logger.info(f"Starting workflow with objective: {objective}")
        self.state.task_exchanges.append(TaskExchange(role="user", content=objective))

        try:
            main_assistant = create_assistant(
                "MainAssistant",
                self.settings.main_assistant_model,
                "You are an expert task coordinator and synthesizer.",
                additional_tools=self.settings.additional_tools,
            )
            refiner_assistant = create_assistant(
                "RefinerAssistant",
                self.settings.refiner_assistant_model,
                "You are an expert at synthesizing and refining task results.",
                additional_tools=self.settings.additional_tools,
            )

            if use_case:
                if use_case not in self.use_case_prompts:
                    raise WorkflowError(f"Plugin '{use_case}' not found")
                prompt = self.use_case_prompts[use_case](objective)
            else:
                prompt = self._generate_main_prompt(objective)

            plan_result: PlanResponse = await self.workers.plan_tasks(prompt, main_assistant)

            if plan_result.objective_completion:
                final_output = plan_result.explanation
                self.state.task_exchanges.append(
                    TaskExchange(role="main_assistant", content=final_output)
                )
            else:
                tasks = plan_result.tasks if plan_result.tasks else []
                self.state.task_exchanges.append(
                    TaskExchange(role="main_assistant", content="\n".join([t.task for t in tasks]))
                )

                results = await self.workers.process_tasks(tasks)
                for result in results:
                    self.state.tasks.append(
                        Task(task=result.task, prompt=result.prompt, result=result.result)
                    )
                    self.state.task_exchanges.append(
                        TaskExchange(role="sub_assistant", content=result.result)
                    )

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

    def _generate_main_prompt(self, objective: str) -> str:
        if self.settings.custom_prompt_template:
            return self.settings.custom_prompt_template.format(objective=objective)

        return f"""
        Analyze the following objective and determine if it requires subtask decomposition:

        Objective: {objective}

        If the objective can be accomplished without subtask decomposition, provide a concise solution.
        If subtask decomposition is needed, break it down into {self.settings.num_workers} subtasks.

        For each subtask, include:
        1. A clear, concise title
        2. A detailed description of what needs to be done
        3. Any specific instructions or considerations

        Your response will be used to guide the task execution, so be thorough and specific.
        """

    def _save_exchange_log(self, objective: str, final_output: str):
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
