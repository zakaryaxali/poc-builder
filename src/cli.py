"""POC Builder CLI - Generate React/Vite frontends from natural language requirements."""

import os
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.design_system.loader import get_default_design_system
from src.generator.component_generator import ComponentGenerator
from src.generator.parser import RequirementsParser
from src.generator.scaffold import ProjectScaffolder
from src.llm.claude import ClaudeClient

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """POC Builder - Generate interactive React frontends from requirements."""
    pass


@main.command()
@click.argument("requirements", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default="./output",
    help="Output directory for generated project",
)
@click.option(
    "--name",
    "-n",
    default="my-app",
    help="Project name",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
)
def generate(
    requirements: str, output: str, name: str, api_key: str | None
) -> None:
    """Generate a React/Vite project from requirements."""
    try:
        # Validate API key
        if not api_key and not os.getenv("ANTHROPIC_API_KEY"):
            console.print(
                "[red]Error: Anthropic API key required. "
                "Set ANTHROPIC_API_KEY environment variable or use --api-key[/red]"
            )
            raise click.Abort()

        output_path = Path(output)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Load Quantum design system
            task = progress.add_task("Loading Quantum design system...", total=None)
            ds = get_default_design_system()
            console.print(f"[green]✓[/green] Using Quantum design system")

            # Initialize Claude client
            progress.update(task, description="Initializing Claude client...")
            client = ClaudeClient(api_key=api_key)
            console.print("[green]✓[/green] Claude client initialized")

            # Parse requirements
            progress.update(task, description="Parsing requirements...")
            parser = RequirementsParser(client)
            spec = parser.parse_from_file(requirements)
            console.print(f"[green]✓[/green] Parsed {len(spec.components)} components")

            # Create base project
            progress.update(task, description="Creating project structure...")
            scaffolder = ProjectScaffolder()
            scaffolder.create_project(output_path, name, ds)
            console.print(f"[green]✓[/green] Created project structure in {output}")

            # Generate components
            progress.update(task, description="Generating components...")
            generator = ComponentGenerator(client, ds)
            generator.generate_project(spec, output_path)
            console.print(f"[green]✓[/green] Generated all components")

            progress.update(task, description="Complete!", total=1, completed=1)

        console.print(f"\n[bold green]✓ Project created successfully![/bold green]")
        console.print(f"\nNext steps:")
        console.print(f"  cd {output}")
        console.print(f"  npm install")
        console.print(f"  npm run dev")

    except FileExistsError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]Hint: Choose a different output directory with --output[/yellow]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    main()
