import os
import time
from typing import Any, List, Optional

import vertexai
from dotenv import load_dotenv
from phi.assistant import Assistant
from phi.llm.anthropic import Claude
from phi.llm.gemini import Gemini
from phi.llm.openai import OpenAIChat
from phi.tools.tavily import TavilyTools

from src.config import settings
from src.utils.exceptions import AssistantError
from src.utils.logging import setup_logging

load_dotenv()
logger = setup_logging()

output_dir = os.path.join(os.getcwd(), "output")
os.makedirs(output_dir, exist_ok=True)

try:
    vertexai.init(project=settings.PROJECT_ID, location=settings.LOCATION)
except Exception as e:
    logger.error(f"Error initializing VertexAI: {str(e)}")


def create_file(file_path: str, content: str):
    full_path = os.path.join(output_dir, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    return f"File created: {full_path}"


def read_file(file_path: str):
    full_path = os.path.join(output_dir, file_path)
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            return f.read()
    return f"File not found: {full_path}"


def list_files(directory: str = ""):
    full_path = os.path.join(output_dir, directory)
    if os.path.exists(full_path):
        files = os.listdir(full_path)
        return ", ".join(files) if files else "No files found"
    return f"Directory not found: {full_path}"


def create_assistant(
    name: str,
    model: str,
    description: str = "You are a helpful assistant.",
    additional_tools: Optional[List] = None,
    **kwargs: Any,
) -> Assistant:
    try:
        if model.startswith("gemini"):
            llm = Gemini(model=model)
        elif model.startswith("claude"):
            llm = Claude(model=model, api_key=settings.ANTHROPIC_API_KEY)
        elif model.startswith("gpt"):
            llm = OpenAIChat(model=model, api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(f"Unsupported model: {model}")

        tools = [
            TavilyTools(api_key=settings.TAVILY_API_KEY),
            create_file,
            read_file,
            list_files,
        ]

        if additional_tools:
            tools.extend(additional_tools)

        assistant_kwargs = {
            "name": name,
            "llm": llm,
            "description": description,
            "tools": tools,
            "debug_mode": False,
            **kwargs,
        }

        return Assistant(**assistant_kwargs)
    except Exception as e:
        logger.error(f"Error creating assistant {name} with model {model}: {str(e)}")
        raise AssistantError(f"Error creating assistant {name} with model {model}: {str(e)}")


def get_full_response(assistant: Assistant, prompt: str, max_retries=3, delay=2) -> str:
    for attempt in range(max_retries):
        try:
            response = assistant.run(prompt, stream=False)
            if isinstance(response, str):
                return response
            elif isinstance(response, list):
                return " ".join(map(str, response))
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise AssistantError(
                    f"Max retries reached. Could not get a response from the assistant: {str(e)}"
                )

    raise AssistantError("Max retries reached. Could not get a response from the assistant.")
