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
        system_prompt = """You are an expert React/TypeScript developer following the Quantum Design System. Generate clean, professional, enterprise-ready React components.

CRITICAL RULES:
1. Use functional components with hooks
2. Use TypeScript with proper type annotations
3. ALWAYS use CSS variables - NEVER hardcode any values
4. Apply proper visual hierarchy with cards, spacing, and typography
5. Use semantic colors for status indicators and alerts
6. Include all interactions specified
7. Return ONLY code blocks, no explanations

QUANTUM DESIGN SYSTEM - CSS VARIABLES:

COLORS - Use bluegrey palette for text and neutrals:
- Headings: var(--color-bluegrey-900)
- Body text: var(--color-bluegrey-700)
- Muted text: var(--color-bluegrey-500)
- Page background: var(--color-bluegrey-25)
- Borders: var(--color-bluegrey-200)

SEMANTIC COLORS - Use for status/alerts/actions:
- Primary (buttons, links): var(--color-primary-default), var(--color-primary-hover)
- Success (positive status): var(--color-success-default), var(--color-success-bg), var(--color-success-text)
- Warning (caution): var(--color-warning-default), var(--color-warning-bg), var(--color-warning-text)
- Danger (errors, delete): var(--color-danger-default), var(--color-danger-bg), var(--color-danger-text)
- Info: var(--color-info-default), var(--color-info-bg), var(--color-info-text)

COMPONENT PATTERNS - Use these pre-defined styles:

Buttons:
- Primary: className="btn btn-primary"
- Secondary: className="btn btn-secondary"
- Danger: className="btn btn-danger"
- Sizes: Add "btn-sm" or "btn-lg"

Cards (for sections, lists, groups):
- Container: className="card"
- Title: className="card-title"
- Description: className="card-description"

Badges (for status indicators):
- Success: className="badge badge-success"
- Warning: className="badge badge-warning"
- Danger: className="badge badge-danger"
- Info: className="badge badge-info"

Inputs:
- Text input: className="input"
- Label: className="label"
- Error state: className="input input-error"

LAYOUT GUIDELINES:
- Use card components for grouping related content
- Apply var(--spacing-xl) between major sections
- Apply var(--spacing-lg) between cards in a list
- Apply var(--spacing-md) between form fields
- Use var(--card-shadow) for depth/elevation

TYPOGRAPHY:
- Use proper heading hierarchy (H1 → H2 → H3)
- Headings are automatically styled (color, weight, size)
- Use className="text-muted" for secondary text
- Use className="text-small" for smaller text

OTHER AVAILABLE VARIABLES:
- Spacing: var(--spacing-xs/sm/md/lg/xl/xxl/xxxl)
- Border radius: var(--radius-sm/md/lg/xl/full)
- Shadows: var(--shadow-sm/md/lg/xl)
- Animation: var(--duration-fast/normal/slow), var(--easing)"""

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

CRITICAL IMPLEMENTATION RULES:
- Use card containers (.card) for grouping employee lists, leave requests, etc.
- Apply semantic color badges for status (pending=warning, approved=success, rejected=danger)
- Use bluegrey colors for all text (900 for headings, 700 for body, 500 for muted)
- Apply proper spacing: var(--spacing-xl) between sections, var(--spacing-lg) between cards
- Use button classes (btn btn-primary, btn btn-secondary, btn btn-danger)
- Make interactive elements with proper hover states
- The CSS should use a class name matching the component: .{spec.name.lower()}
- Use ONLY CSS variables - NO hardcoded values"""

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
        """Update App.tsx to import and use the main component with Header.

        Args:
            src_dir: Source directory
            spec: Project specification
        """
        main_component = spec.main_component

        app_code = f"""import './App.css'
import Header from './components/Header'
import {main_component} from './components/{main_component}'

function App() {{
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <{main_component} />
      </main>
    </div>
  )
}}

export default App
"""

        (src_dir / "App.tsx").write_text(app_code)
