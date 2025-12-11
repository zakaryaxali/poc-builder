"""Project scaffolding - create base Vite/React project from template."""

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.design_system.models import DesignSystem


class ProjectScaffolder:
    """Handles creation of base Vite/React project structure."""

    def __init__(self, template_dir: Path | None = None):
        """Initialize the scaffolder.

        Args:
            template_dir: Path to template directory (defaults to templates/vite-react)
        """
        if template_dir is None:
            self.template_dir = Path(__file__).parent.parent.parent / "templates" / "vite-react"
        else:
            self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,
        )

    def create_project(
        self,
        output_dir: Path,
        project_name: str,
        design_system: DesignSystem,
    ) -> None:
        """Create a new Vite/React project from template.

        Args:
            output_dir: Directory to create the project in
            project_name: Name of the project
            design_system: Design system configuration to inject

        Raises:
            FileExistsError: If output directory already exists
        """
        output_path = Path(output_dir)

        if output_path.exists():
            raise FileExistsError(f"Output directory already exists: {output_dir}")

        # Create output directory structure
        output_path.mkdir(parents=True)
        (output_path / "src").mkdir()
        (output_path / "src" / "components").mkdir()
        (output_path / "public").mkdir()

        # Prepare template context with all design system tokens
        context = {
            "project_name": project_name,
            "colors": design_system.colors.model_dump(),
            "semantic_colors": design_system.semantic_colors.model_dump(),
            "typography": design_system.typography.model_dump(),
            "spacing": design_system.spacing.model_dump(),
            "border_width": design_system.border_width.model_dump(),
            "border_radius": design_system.border_radius.model_dump(),
            "shadows": design_system.shadows.model_dump(),
            "animation": design_system.animation.model_dump(),
            "layout": design_system.layout.model_dump(),
            "breakpoints": design_system.breakpoints.model_dump(),
            "header": design_system.header.model_dump(),
            "button": design_system.button.model_dump(),
            "card": design_system.card.model_dump(),
            "badge": design_system.badge.model_dump(),
            "input": design_system.input.model_dump(),
        }

        # Process template files
        self._process_template_file("package.json.j2", output_path / "package.json", context)
        self._process_template_file("index.html", output_path / "index.html", context)
        self._process_template_file("src/main.tsx.j2", output_path / "src" / "main.tsx", context)
        self._process_template_file("src/index.css.j2", output_path / "src" / "index.css", context)
        self._process_template_file("src/App.css.j2", output_path / "src" / "App.css", context)

        # Generate Header component
        self._process_template_file("src/components/Header.tsx.j2", output_path / "src" / "components" / "Header.tsx", context)
        self._process_template_file("src/components/Header.css.j2", output_path / "src" / "components" / "Header.css", context)

        # Copy static files
        self._copy_static_file("vite.config.ts", output_path / "vite.config.ts")
        self._copy_static_file("tsconfig.json", output_path / "tsconfig.json")
        self._copy_static_file("tsconfig.node.json", output_path / "tsconfig.node.json")
        self._copy_static_file("public/thales-logo.svg", output_path / "public" / "thales-logo.svg")

        # Create .gitignore
        gitignore_content = """node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
"""
        (output_path / ".gitignore").write_text(gitignore_content)

    def _process_template_file(
        self, template_path: str, output_path: Path, context: dict
    ) -> None:
        """Render a Jinja2 template and write to output.

        Args:
            template_path: Path to template file relative to template_dir
            output_path: Path to write rendered output
            context: Template context variables
        """
        template = self.jinja_env.get_template(template_path)
        rendered = template.render(**context)
        output_path.write_text(rendered)

    def _copy_static_file(self, source_path: str, output_path: Path) -> None:
        """Copy a non-template file directly.

        Args:
            source_path: Path relative to template_dir
            output_path: Destination path
        """
        source = self.template_dir / source_path
        if source.exists():
            shutil.copy2(source, output_path)
