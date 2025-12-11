# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

POC Builder is a Python-based tool that generates interactive React/Vite frontends based on natural language requirements. It uses CrewAI or LangChain for orchestration, is LLM-agnostic, enforces a predefined design system, and supports iterative feedback loops. All generated projects must build and run without errors.

## Tech Stack

- **Tool Language**: Python
- **Orchestration**: CrewAI or LangChain
- **Generated Output**: React + Vite + TypeScript
- **LLM Support**: Provider-agnostic (OpenAI, Anthropic, local models, etc.)

## Core Architecture

### Python Backend (POC Builder Tool)

**LLM Abstraction Layer**
- Abstract LLM provider interface for any model (OpenAI, Anthropic, Ollama, etc.)
- Provider implementations as pluggable modules
- Runtime provider selection via configuration

**Agents/Chains** (CrewAI or LangChain)
- Requirements Analysis Agent: Parses natural language into structured specs
- Component Design Agent: Plans component hierarchy based on requirements
- Code Generation Agent: Generates React/TypeScript code following design system
- Validation Agent: Ensures code builds and adheres to design system
- Feedback Processing Agent: Applies iterative updates based on user input

**Design System Management**
- Python-based design token definitions (colors, typography, spacing)
- Template system for injecting design system into generated projects
- Validation rules to enforce design system compliance

**Code Generation Pipeline**
1. Parse requirements into structured data
2. Generate component structure plan
3. Generate React components with TypeScript
4. Generate event handlers and state logic
5. Inject design system configuration
6. Scaffold Vite project with generated code
7. Validate build succeeds
8. Return runnable project

**Feedback Loop**
- Parse user feedback into actionable changes
- Apply targeted updates without full regeneration
- Re-validate builds after changes
- Maintain iteration history

### Generated Projects (React/Vite)

Each generated project includes:
- Vite configuration with React + TypeScript
- Design system (theme tokens, styled components)
- Generated components following design system
- Interactive logic (event handlers, state management)
- All dependencies in package.json
- Ready to `npm install && npm run dev`

## Key Commands

### POC Builder Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the builder CLI
python -m poc_builder --requirements "input.txt" --design-system "config.json"

# Run tests
pytest

# Run specific test
pytest tests/test_generator.py

# Type checking
mypy src/

# Linting
ruff check src/
```

### Generated Vite/React Projects
```bash
npm install      # Install dependencies
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
```

## Design System Configuration

Design systems are defined in JSON/YAML format with:
- Color palette (primary, secondary, semantic colors)
- Typography (font families, sizes, weights, line heights)
- Spacing scale (consistent padding/margin values)
- Border radius values
- Shadow definitions
- Breakpoints for responsive design

The tool injects this configuration into every generated project as:
- CSS variables
- TypeScript theme object
- Styled-components theme (if using styled-components)

## LLM Provider Integration

When adding LLM provider support:
- Implement the `LLMProvider` abstract base class
- Handle authentication/API keys via environment variables
- Implement retry logic and rate limiting
- Support streaming for real-time feedback
- Include design system context in all prompts
- Use structured outputs where supported (e.g., JSON mode)

## Code Generation Rules

All generated React code must:
- Use TypeScript with strict mode
- Use functional components and hooks
- Include proper type definitions (no `any` types)
- Use design system tokens exclusively (no hardcoded colors/spacing)
- Implement all interactive features from requirements
- Follow consistent formatting (Prettier-compatible)
- Build with zero errors and zero warnings
- Include proper accessibility attributes

## Feedback Processing

When processing user feedback:
1. Identify which components/features need modification
2. Load the existing generated project
3. Apply targeted changes (prefer surgical edits over full regeneration)
4. Re-run build validation
5. Ensure changes don't break design system compliance
6. Preserve any manual customizations unless explicitly overridden

## Project Structure

```
poc-builder/
├── src/
│   ├── cli.py                     # CLI entry point
│   ├── llm/                       # LLM provider abstractions
│   │   └── claude.py              # Claude API client
│   ├── design_system/             # Design system management
│   │   ├── models.py              # Pydantic models
│   │   └── loader.py              # Loading utilities
│   ├── generator/                 # React/Vite code generation
│   │   ├── parser.py              # Requirements → specs
│   │   ├── component_generator.py # Component code generation
│   │   └── scaffold.py            # Project scaffolding
│   ├── validator/                 # Build and compliance validation
│   └── feedback/                  # Feedback parsing (TODO)
├── templates/
│   └── vite-react/                # Base Vite/React template
├── design_systems/                # Example design system configs
│   └── default.json
├── examples/                      # Example requirements
│   ├── todo-app.txt
│   └── contact-form.txt
├── tests/                         # Test suite
└── pyproject.toml                 # Python project config
```

## Current Implementation Status

**Completed:**
- ✅ Python project setup with uv
- ✅ Design system JSON schema and default config
- ✅ Claude API wrapper with retry logic
- ✅ Vite/React template with CSS variables
- ✅ Project scaffolding from templates
- ✅ Requirements parser (natural language → component specs)
- ✅ React component generator
- ✅ CLI with basic generation command
- ✅ Example requirements files

**TODO (Phase 2):**
- Interactive feedback mode for iterative refinement
- TypeScript syntax validation
- Full build validation (npm install && npm run build)
- Feedback parsing and code updating
- CrewAI/LangChain orchestration
- Additional LLM provider support
