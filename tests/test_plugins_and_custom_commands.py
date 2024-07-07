from unittest.mock import AsyncMock, MagicMock, patch

import pluggy
import pytest
from typer.testing import CliRunner

from src.main import app
from src.orchestrator import Orchestrator, OrchestratorSettings
from src.plugin_manager import PluginManager, PluginSpec, hookimpl

runner = CliRunner()


def test_custom_prompt_command_option():
    with patch("src.main.Orchestrator") as mock_orchestrator, patch(
        "src.main.asyncio.run"
    ) as mock_asyncio_run:
        mock_orchestrator.return_value.run_workflow = AsyncMock(return_value="Test output")
        mock_asyncio_run.return_value = "Test output"
        custom_prompt = "Custom prompt: {objective}"
        result = runner.invoke(
            app, ["run-workflow", "Test objective", "--custom-prompt", custom_prompt]
        )
        assert result.exit_code == 0
        assert "Using custom prompt template" in result.output
        mock_orchestrator.assert_called_once()
        settings = mock_orchestrator.call_args[1]["settings"]
        assert settings.custom_prompt_template == custom_prompt


def test_plugin_manager_load_plugins():
    class TestPlugin:
        @hookimpl
        def get_use_case_prompt(self, objective: str) -> str:
            return f"Test prompt for: {objective}"

    pm = pluggy.PluginManager("saa_orchestrator")
    pm.add_hookspecs(PluginSpec)
    test_plugin = TestPlugin()
    pm.register(test_plugin, name="TestPlugin")

    plugin_manager = PluginManager()
    plugin_manager.manager = pm  # Replace the internal manager with our test manager

    prompts = plugin_manager.get_use_case_prompts()
    assert "TestPlugin" in prompts
    assert prompts["TestPlugin"]("test objective") == "Test prompt for: test objective"


@pytest.mark.asyncio
async def test_orchestrator_with_plugin():
    class TestPlugin:
        @hookimpl
        def get_use_case_prompt(self, objective: str) -> str:
            return f"Test plugin prompt for: {objective}"

    pm = pluggy.PluginManager("saa_orchestrator")
    pm.add_hookspecs(PluginSpec)
    test_plugin = TestPlugin()
    pm.register(test_plugin, name="TestPlugin")

    plugin_manager = PluginManager()
    plugin_manager.manager = pm

    orchestrator = Orchestrator(settings=OrchestratorSettings())
    orchestrator.use_case_prompts = plugin_manager.get_use_case_prompts()

    with patch("src.orchestrator.create_assistant") as mock_create_assistant, patch(
        "src.workers.SAAsWorkers.plan_tasks"
    ) as mock_plan_tasks:

        mock_main_assistant = MagicMock()
        mock_refiner_assistant = MagicMock()
        mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

        mock_plan_tasks.return_value = MagicMock(
            objective_completion=True, explanation="Test result"
        )

        result = await orchestrator.run_workflow("Test objective", use_case="TestPlugin")

        assert result == "Test result"
        mock_plan_tasks.assert_called_once()
        assert "Test plugin prompt for: Test objective" in mock_plan_tasks.call_args[0][0]


@pytest.mark.asyncio
async def test_orchestrator_with_custom_prompt():
    custom_prompt = "Custom prompt: {objective}"
    orchestrator = Orchestrator(settings=OrchestratorSettings(custom_prompt_template=custom_prompt))

    with patch("src.orchestrator.create_assistant") as mock_create_assistant, patch(
        "src.workers.SAAsWorkers.plan_tasks"
    ) as mock_plan_tasks:

        mock_main_assistant = MagicMock()
        mock_refiner_assistant = MagicMock()
        mock_create_assistant.side_effect = [mock_main_assistant, mock_refiner_assistant]

        mock_plan_tasks.return_value = MagicMock(
            objective_completion=True, explanation="Test result"
        )

        result = await orchestrator.run_workflow("Test objective")

        assert result == "Test result"
        mock_plan_tasks.assert_called_once()
        assert "Custom prompt: Test objective" in mock_plan_tasks.call_args[0][0]
