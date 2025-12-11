# POC Builder

Build interactive React/Vite frontends from natural language requirements using AI.

## Features

- **LLM-Agnostic**: Currently supports Claude (Anthropic), easily extensible to other providers
- **Design System Enforcement**: All generated code follows a predefined design system using CSS variables
- **Type-Safe**: Generates TypeScript components with proper type annotations
- **Interactive**: Generates fully functional components with event handlers and state management
- **Build-Ready**: Generated projects can be built and run immediately

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd poc-builder

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install --native-tls -e ".[dev]"
```

## Quick Start

1. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

2. Create a requirements file (see `examples/` for templates):
```bash
cat > requirements.txt << EOF
Build a simple counter app with:
- A display showing the current count (starts at 0)
- An increment button (+)
- A decrement button (-)
- A reset button
EOF
```

3. Generate your project:
```bash
poc-builder generate requirements.txt -o my-counter-app -n counter
```

4. Run the generated project:
```bash
cd my-counter-app
npm install
npm run dev
```

## Usage

### Basic Generation

```bash
poc-builder generate <requirements-file> [OPTIONS]
```

**Options:**
- `-o, --output DIR`: Output directory (default: `./output`)
- `-n, --name TEXT`: Project name (default: `my-app`)
- `--api-key TEXT`: Anthropic API key (or set `ANTHROPIC_API_KEY` env var)

### Design System

All generated projects automatically use the **Quantum** design system, which includes:

- **Brand Colors**: Quantum blue (#041295) and cyan (#66D7EB) with hover states
- **Typography**: Inter font family for headings and body text
- **Spacing**: Consistent spacing scale from 4px to 64px
- **Components**: Predefined border radius, shadows, and animation timing
- **Layout**: 1368px max width with responsive breakpoints

All generated components will follow these design guidelines automatically using CSS variables.

## Examples

Check the `examples/` directory for sample requirements:
- `todo-app.txt` - Todo list application
- `contact-form.txt` - Contact form with validation

Try them out:
```bash
poc-builder generate examples/todo-app.txt -o todo-app -n todo
```

## Development

```bash
# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/

# Format code
ruff format src/
```

## Project Structure

```
poc-builder/
├── src/
│   ├── cli.py                    # CLI entry point
│   ├── llm/                      # LLM provider integrations
│   │   └── claude.py             # Claude API wrapper
│   ├── design_system/            # Design system management
│   │   ├── models.py             # Pydantic models for validation
│   │   └── loader.py             # Loading utilities
│   ├── generator/                # Code generation
│   │   ├── parser.py             # Requirements → component specs
│   │   ├── component_generator.py # Spec → React code
│   │   └── scaffold.py           # Project scaffolding
│   └── validator/                # Code validation
├── templates/                    # Vite/React project templates
│   └── vite-react/              # Base template
├── design_systems/               # Design system configurations
│   └── default.json             # Default design system
├── examples/                     # Example requirements
└── tests/                        # Test suite
```

## How It Works

1. **Requirements Parsing**: Natural language requirements are sent to Claude, which analyzes them and returns a structured specification of components to build

2. **Project Scaffolding**: A base Vite + React + TypeScript project is created from templates

3. **Design System Injection**: The design system configuration is converted to CSS variables in the generated project

4. **Component Generation**: Each component specification is sent to Claude, which generates React/TypeScript code that uses only design system variables

5. **Validation**: Generated code is validated for TypeScript syntax (full build validation coming soon)

6. **Output**: A complete, runnable React project ready for `npm install && npm run dev`

## Roadmap

- [ ] Interactive feedback mode for iterative refinement
- [ ] Full build validation
- [ ] Support for additional LLM providers (OpenAI, Ollama)
- [ ] More sophisticated component generation (routing, API integration)
- [ ] Web UI for non-CLI users
- [ ] Pre-built component libraries (shadcn/ui, MUI integration)

## License

MIT
