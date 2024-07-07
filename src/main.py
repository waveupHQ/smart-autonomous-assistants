import asyncio
import os

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from src.config import settings
from src.orchestrator import Orchestrator, OrchestratorSettings
from src.plugin_manager import plugin_manager

app = typer.Typer()

# Define and create plugin folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
plugin_folder = os.path.join(project_root, "plugins")
os.makedirs(plugin_folder, exist_ok=True)


# Load plugins
try:
    plugin_manager.load_plugins(plugin_folder)
except Exception as e:
    rprint(f"[bold red]Error loading plugins: {str(e)}[/bold red]")


@app.command()
def run_workflow(
    objective: list[str] = typer.Argument(
        ..., help="The objective for the workflow. Can be multiple words."
    ),
    plugin: str = typer.Option(
        None, "--plugin", "-p", help="Use a specific plugin for the workflow."
    ),
    num_workers: int = typer.Option(
        settings.NUM_WORKERS, "--workers", "-w", help="Number of workers for parallel processing."
    ),
    main_model: str = typer.Option(
        settings.MAIN_ASSISTANT, "--main-model", help="Model for the main assistant."
    ),
    sub_model: str = typer.Option(
        settings.SUB_ASSISTANT, "--sub-model", help="Model for the sub assistants."
    ),
    refiner_model: str = typer.Option(
        settings.REFINER_ASSISTANT, "--refiner-model", help="Model for the refiner assistant."
    ),
    custom_prompt_template: str = typer.Option(
        None, "--custom-prompt", help="Custom prompt template to use for the main assistant."
    ),
):
    """
    Run the SAA Orchestrator workflow with the given objective.
    """
    full_objective = " ".join(objective)
    try:
        rprint("[bold]Starting SAA Orchestrator[/bold]")
        if plugin:
            rprint(f"[bold yellow]Using plugin: {plugin}[/bold yellow]")
        if custom_prompt_template:
            rprint("[bold yellow]Using custom prompt template[/bold yellow]")
        orchestrator_settings = OrchestratorSettings(
            main_assistant_model=main_model,
            sub_assistant_model=sub_model,
            refiner_assistant_model=refiner_model,
            num_workers=num_workers,
            custom_prompt_template=custom_prompt_template,
        )

        orchestrator = Orchestrator(settings=orchestrator_settings)

        result = asyncio.run(orchestrator.run_workflow(full_objective, use_case=plugin))

        rprint("\n[bold green]Workflow completed![/bold green]")
        rprint("\n[bold]Final Output:[/bold]")
        rprint(result)
        rprint("\n[bold blue]Exchange log saved to 'exchange_log.md'[/bold blue]")
    except Exception as e:
        rprint(f"[bold red]An error occurred:[/bold red] {str(e)}")


@app.command()
def list_plugins():
    """
    List all available plugins.
    """
    console = Console()

    rprint(f"[bold]Plugin folder:[/bold] {plugin_folder}")

    plugins = plugin_manager.get_use_case_prompts()

    if not plugins:
        rprint(
            "[yellow]No plugins found. Make sure plugin files end with '_plugin.py' and contain a valid plugin class.[/yellow]"
        )
        return

    table = Table(title="Available Plugins")
    table.add_column("Plugin Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")

    for plugin_name, plugin_func in plugins.items():
        description = (
            plugin_func.__doc__.strip().split("\n")[0]
            if plugin_func.__doc__
            else "No description available"
        )
        table.add_row(plugin_name, description)

    console.print(table)


if __name__ == "__main__":
    app()
