"""React component code generation using Claude."""

from pathlib import Path

from src.design_system.models import DesignSystem
from src.llm.claude import ClaudeClient
from src.generator.parser import ComponentSpec, ProjectSpec


class ComponentGenerator:
    """Generate React/TypeScript component code."""

    def __init__(self, claude_client: ClaudeClient, design_system: DesignSystem):
        """Initialize the generator.

        Args:
            claude_client: Claude API client
            design_system: Design system configuration
        """
        self.client = claude_client
        self.design_system = design_system

    def generate_component(self, spec: ComponentSpec) -> tuple[str, str]:
        """Generate React component code and CSS from specification.

        Args:
            spec: Component specification

        Returns:
            Tuple of (tsx_code, css_code)
        """
        system_prompt = """You are an expert React/TypeScript developer. Generate clean, type-safe React components.

Follow these strict rules:
1. Use functional components with hooks
2. Use TypeScript with proper type annotations
3. Use CSS variables from the design system (NEVER hardcode colors, spacing, etc.)
4. Follow React best practices
5. Include all interactions specified
6. Write clean, readable code with good naming
7. Return ONLY the code, no explanations

Available CSS variables:

Colors:
- Primary: var(--color-primary), var(--color-primary-hover), var(--color-primary-light), var(--color-primary-dark)
- Secondary: var(--color-secondary), var(--color-secondary-hover)
- Neutral: var(--color-background), var(--color-surface), var(--color-border), var(--color-divider)
- Text: var(--color-text-heading), var(--color-text-body), var(--color-text-muted), var(--color-text-disabled)
- Semantic: var(--color-success), var(--color-error), var(--color-warning), var(--color-info)

Typography:
- Families: var(--font-family-heading), var(--font-family-body), var(--font-family-mono)
- Sizes: var(--font-size-h1/h2/h3/h4/h5/h6), var(--font-size-body-large/body/body-small/caption)
- Weights: var(--font-weight-light/regular/medium/semibold/bold)
- Line heights: var(--line-height-tight/normal/relaxed)
- Letter spacing: var(--letter-spacing-tight/normal/wide)

Spacing: var(--spacing-xs/sm/md/lg/xl/xxl/xxxl)

Border widths: var(--border-width-thin/medium/thick)

Border radius: var(--radius-none/sm/md/lg/xl/full)

Shadows: var(--shadow-none/sm/md/lg/xl)

Animation: var(--duration-fast/normal), var(--easing)

Layout: var(--max-width), var(--section-padding-vertical/horizontal), var(--grid-gap)"""

        # Build prompt with component spec
        prompt = f"""Generate a React component with these specifications:

Name: {spec.name}
Description: {spec.description}
Props: {spec.props if spec.props else 'None'}
State: {spec.state if spec.state else 'None'}
Interactions: {', '.join(spec.interactions) if spec.interactions else 'None'}
Child components: {', '.join(spec.children) if spec.children else 'None'}

Generate two code blocks:

1. TypeScript component (.tsx):
```tsx
// Component code here
```

2. CSS file (.css):
```css
/* Styles here using CSS variables */
```

IMPORTANT:
- Use ONLY CSS variables for all styling (colors, spacing, typography, etc.)
- The CSS should use a class name matching the component: .{spec.name.lower()}
- Implement ALL specified interactions with proper event handlers
- Use proper TypeScript types for all props, state, and handlers
- Make the component fully functional and interactive"""

        response = self.client.generate(prompt=prompt, system=system_prompt, temperature=0.5)

        # Extract code blocks
        import re

        tsx_match = re.search(r"```tsx\n(.*?)\n```", response, re.DOTALL)
        css_match = re.search(r"```css\n(.*?)\n```", response, re.DOTALL)

        if not tsx_match:
            raise ValueError(f"Failed to extract TSX code from response for {spec.name}")

        tsx_code = tsx_match.group(1).strip()
        css_code = css_match.group(1).strip() if css_match else f"/* Styles for {spec.name} */"

        return tsx_code, css_code

    def generate_project(self, spec: ProjectSpec, output_dir: Path) -> None:
        """Generate all components for a project.

        Args:
            spec: Complete project specification
            output_dir: Directory to write component files to
        """
        src_dir = output_dir / "src"
        components_dir = src_dir / "components"
        components_dir.mkdir(exist_ok=True)

        # Generate each component
        for component_spec in spec.components:
            print(f"Generating {component_spec.name}...")

            tsx_code, css_code = self.generate_component(component_spec)

            # Write component files
            component_file = components_dir / f"{component_spec.name}.tsx"
            css_file = components_dir / f"{component_spec.name}.css"

            component_file.write_text(tsx_code)
            css_file.write_text(css_code)

        # Update App.tsx to use the main component
        self._update_app_component(src_dir, spec)

    def _update_app_component(self, src_dir: Path, spec: ProjectSpec) -> None:
        """Update App.tsx to import and use the main component.

        Args:
            src_dir: Source directory
            spec: Project specification
        """
        main_component = spec.main_component

        app_code = f"""import './App.css'
import {main_component} from './components/{main_component}'

function App() {{
  return (
    <div className="app">
      <{main_component} />
    </div>
  )
}}

export default App
"""

        (src_dir / "App.tsx").write_text(app_code)
