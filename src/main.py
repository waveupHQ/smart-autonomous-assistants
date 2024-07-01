import typer
from rich import print as rprint

from src.orchestrator import Orchestrator

app = typer.Typer()


@app.command()
def run_workflow(
    objective: list[str] = typer.Argument(
        ..., help="The objective for the workflow. Can be multiple words."
    )
):
    """
    Run the SAA Orchestrator workflow with the given objective.
    """
    full_objective = " ".join(objective)
    try:
        rprint("[bold]Starting SAA Orchestrator[/bold]")
        orchestrator = Orchestrator()
        result = orchestrator.run_workflow(full_objective)

        rprint("\n[bold green]Workflow completed![/bold green]")
        rprint("\n[bold]Final Output:[/bold]")
        rprint(result)
        rprint("\n[bold blue]Exchange log saved to 'exchange_log.md'[/bold blue]")
    except ValueError as e:
        rprint(f"[bold red]Error:[/bold red] {str(e)}")
        rprint("Please make sure you have set the required API keys in your .env file.")
    except Exception as e:
        rprint(f"[bold red]An unexpected error occurred:[/bold red] {str(e)}")


if __name__ == "__main__":
    app()
