"""POC Builder CLI - Generate React/Vite frontends from natural language requirements."""

import os
import subprocess
import time
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.design_system.loader import get_default_design_system
from src.design_system.models import DesignSystem
from src.generator.component_generator import ComponentGenerator
from src.generator.parser import RequirementsParser
from src.generator.scaffold import ProjectScaffolder
from src.llm.claude import ClaudeClient

# Load environment variables from .env file
load_dotenv()

console = Console()


def _run_npm_command(command: str, cwd: Path) -> subprocess.CompletedProcess:
    """Run an npm command in the specified directory.

    Args:
        command: npm command to run (e.g., "install", "run build")
        cwd: Working directory to run command in

    Returns:
        CompletedProcess with result
    """
    return subprocess.run(
        f"npm {command}",
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _display_metrics(start_time: float, client: ClaudeClient) -> None:
    """Display execution metrics (time and token usage).

    Args:
        start_time: Start time from time.time()
        client: Claude client with token usage tracking
    """
    end_time = time.time()
    execution_time = end_time - start_time
    token_usage = client.get_token_usage()

    # Format time
    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)
    time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

    # Format tokens with thousand separators
    input_tokens = f"{token_usage['input_tokens']:,}"
    output_tokens = f"{token_usage['output_tokens']:,}"
    total_tokens = f"{token_usage['total_tokens']:,}"

    console.print(f"\n[bold cyan]📊 Metrics:[/bold cyan] ⏱  {time_str} | 🪙 {total_tokens} tokens ({input_tokens} in / {output_tokens} out)")


def _attempt_simple_typescript_fix(project_dir: Path, error_output: str) -> bool:
    """Attempt to fix simple TypeScript errors automatically.

    Args:
        project_dir: Project directory
        error_output: Build error output

    Returns:
        True if a fix was applied, False otherwise
    """
    import re

    # Pattern: TS6133: 'variableName' is declared but its value is never read
    unused_var_pattern = r"TS6133: '(\w+)' is declared but its value is never read"
    file_pattern = r"src/components/(\w+\.tsx):(\d+):(\d+)"

    matches = list(re.finditer(unused_var_pattern, error_output))
    file_matches = list(re.finditer(file_pattern, error_output))

    if matches and file_matches:
        for match, file_match in zip(matches, file_matches):
            unused_var = match.group(1)
            file_name = file_match.group(1)
            file_path = project_dir / "src" / "components" / file_name

            if file_path.exists():
                content = file_path.read_text()
                # Replace the unused variable with underscore prefix
                # Match common patterns: const [x, setX] or const x =
                updated_content = re.sub(
                    rf"\b{unused_var}\b",
                    f"_{unused_var}",
                    content,
                    count=1
                )
                if updated_content != content:
                    file_path.write_text(updated_content)
                    console.print(f"[green]✓[/green] Auto-fixed: Renamed unused variable '{unused_var}' to '_{unused_var}'")
                    return True

    return False


def _attempt_build_fix(
    client: ClaudeClient, project_dir: Path, error_output: str, design_system: DesignSystem
) -> bool:
    """Attempt to fix build errors using Claude.

    Args:
        client: Claude API client
        project_dir: Project directory
        error_output: Build error output (combined stdout + stderr)
        design_system: Design system being used

    Returns:
        True if a fix was attempted, False otherwise
    """
    # First try simple automated fixes
    if _attempt_simple_typescript_fix(project_dir, error_output):
        return True

    try:
        # Extract relevant error information (last 2000 chars to get actual errors)
        error_summary = error_output[-2000:] if len(error_output) > 2000 else error_output

        fix_prompt = f"""A TypeScript/React build failed with this error:

{error_summary}

Analyze the error and provide ONLY the necessary code fixes. For each file that needs fixing:
1. Identify the specific issue
2. Provide the corrected code

Return a JSON array of fixes:
[
  {{
    "file": "relative/path/to/file.tsx",
    "issue": "Brief description",
    "fixed_code": "Complete corrected file content"
  }}
]

Remember:
- Use CSS variables from the design system (var(--color-primary), etc.)
- Ensure proper TypeScript types
- Fix import paths if needed
- Return ONLY valid JSON"""

        response = client.generate_structured(
            prompt=fix_prompt,
            system="You are an expert at fixing TypeScript/React build errors. Provide concise, working fixes.",
        )

        if isinstance(response, list) and len(response) > 0:
            # Apply fixes
            for fix in response:
                file_path = project_dir / fix["file"]
                if file_path.exists():
                    file_path.write_text(fix["fixed_code"])
                    console.print(f"[yellow]→[/yellow] Fixed {fix['file']}: {fix['issue']}")
            return True

    except Exception as e:
        console.print(f"[yellow]⚠[/yellow] Auto-fix error: {e}")

    return False


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
    default=None,
    help="Output directory name inside ./output/ (default: project name)",
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
    requirements: str, output: str | None, name: str, api_key: str | None
) -> None:
    """Generate a React/Vite project from requirements."""
    try:
        # Start timing
        start_time = time.time()

        # Validate API key
        if not api_key and not os.getenv("ANTHROPIC_API_KEY"):
            console.print(
                "[red]Error: Anthropic API key required. "
                "Set ANTHROPIC_API_KEY environment variable or use --api-key[/red]"
            )
            raise click.Abort()

        # Prepend output/ to the path
        if output is None:
            output_path = Path("output") / name
        else:
            # If output starts with "output/", don't prepend it again
            if output.startswith("output/") or output.startswith("output\\"):
                output_path = Path(output)
            else:
                output_path = Path("output") / output

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
            console.print(f"[green]✓[/green] Using model: {client.model}")

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

            # Install dependencies
            progress.update(task, description="Installing dependencies...")
            install_result = _run_npm_command("install", output_path)
            if install_result.returncode != 0:
                console.print("[red]✗[/red] npm install failed")
                console.print(f"[red]Error:[/red] {install_result.stderr[:500]}")
                _display_metrics(start_time, client)
                raise click.Abort()
            console.print(f"[green]✓[/green] Installed dependencies")

            # Build and validate (with retry logic)
            progress.update(task, description="Building project...")
            build_success = False
            max_attempts = 3

            for attempt in range(max_attempts):
                build_result = _run_npm_command("run build", output_path)

                if build_result.returncode == 0:
                    build_success = True
                    break

                console.print(f"[yellow]⚠[/yellow] Build attempt {attempt + 1} failed")

                if attempt < max_attempts - 1:
                    # Try to fix build errors using Claude
                    console.print("[yellow]→[/yellow] Analyzing errors and attempting fix...")
                    # Combine stdout and stderr for complete error context
                    combined_error = build_result.stdout + "\n" + build_result.stderr
                    fix_applied = _attempt_build_fix(
                        client, output_path, combined_error, ds
                    )
                    if not fix_applied:
                        console.print("[yellow]⚠[/yellow] Could not auto-fix, retrying...")

            if build_success:
                console.print(f"[green]✓[/green] Build successful")
            else:
                console.print(f"[red]✗[/red] Build failed after {max_attempts} attempts")
                console.print(f"\n[red]Build errors:[/red]")
                # Show combined output
                combined_error = build_result.stdout + "\n" + build_result.stderr
                console.print(combined_error[-1000:])  # Show last 1000 chars

                # Display metrics before aborting
                _display_metrics(start_time, client)
                raise click.Abort()

            progress.update(task, description="Complete!", total=1, completed=1)

        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Get token usage
        token_usage = client.get_token_usage()

        # Display success message
        console.print(f"\n[bold green]✓ Project created and validated successfully![/bold green]")

        # Display metrics
        console.print(f"\n[bold cyan]📊 Generation Metrics:[/bold cyan]")

        # Format execution time
        if execution_time < 60:
            time_str = f"{execution_time:.1f}s"
        else:
            minutes = int(execution_time // 60)
            seconds = execution_time % 60
            time_str = f"{minutes}m {seconds:.1f}s"

        console.print(f"   ⏱  Execution time: {time_str}")
        console.print(f"   📥 Input tokens:  {token_usage['input_tokens']:,}")
        console.print(f"   📤 Output tokens: {token_usage['output_tokens']:,}")
        console.print(f"   📊 Total tokens:  {token_usage['total_tokens']:,}")

        console.print(f"\n[bold]Project location:[/bold] {output_path}")
        console.print(f"\n[bold]To run your app:[/bold]")
        console.print(f"  cd {output_path}")
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
