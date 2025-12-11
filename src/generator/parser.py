"""Requirements parser - convert natural language to structured component specs."""

from typing import Any

from pydantic import BaseModel, Field

from src.llm.claude import ClaudeClient


class ComponentSpec(BaseModel):
    """Specification for a single React component."""

    name: str = Field(..., description="Component name (PascalCase)")
    description: str = Field(..., description="What the component does")
    props: dict[str, str] = Field(
        default_factory=dict, description="Props with their TypeScript types"
    )
    state: dict[str, str] = Field(default_factory=dict, description="State variables with types")
    interactions: list[str] = Field(
        default_factory=list, description="User interactions (clicks, inputs, etc.)"
    )
    children: list[str] = Field(
        default_factory=list, description="Child component names this uses"
    )


class ProjectSpec(BaseModel):
    """Complete project specification from requirements."""

    description: str = Field(..., description="Overall project description")
    components: list[ComponentSpec] = Field(..., description="List of components to build")
    main_component: str = Field(..., description="Name of the root/main component")


class RequirementsParser:
    """Parse natural language requirements into structured specifications."""

    def __init__(self, claude_client: ClaudeClient):
        """Initialize the parser.

        Args:
            claude_client: Claude API client for LLM calls
        """
        self.client = claude_client

    def parse(self, requirements: str) -> ProjectSpec:
        """Parse requirements text into structured project specification.

        Args:
            requirements: Natural language description of what to build

        Returns:
            Structured project specification

        Raises:
            ValueError: If parsing fails or LLM returns invalid response
        """
        system_prompt = """You are a React application architect. Parse user requirements into a structured component specification.

Analyze the requirements and break them down into React components. For each component, identify:
- Name (PascalCase, descriptive)
- Description (what it does)
- Props (if any, with TypeScript types)
- State (what local state it needs, with types)
- Interactions (user actions like clicks, inputs, form submits)
- Child components it uses

Think about:
- Component composition and reusability
- Proper separation of concerns
- State management (which component owns which state)
- User interactions and event handlers

Respond with JSON only."""

        prompt = f"""Parse these requirements into component specifications:

{requirements}

Return a JSON object with this structure:
{{
  "description": "Brief project description",
  "components": [
    {{
      "name": "ComponentName",
      "description": "What it does",
      "props": {{"propName": "type"}},
      "state": {{"stateName": "type"}},
      "interactions": ["onClick", "onChange", etc],
      "children": ["ChildComponent1", "ChildComponent2"]
    }}
  ],
  "main_component": "App"
}}"""

        try:
            response_dict = self.client.generate_structured(prompt=prompt, system=system_prompt)

            # Validate and parse into Pydantic model
            return ProjectSpec(**response_dict)

        except Exception as e:
            raise ValueError(f"Failed to parse requirements: {e}") from e

    def parse_from_file(self, file_path: str) -> ProjectSpec:
        """Parse requirements from a text file.

        Args:
            file_path: Path to requirements file

        Returns:
            Structured project specification
        """
        with open(file_path) as f:
            requirements = f.read()

        return self.parse(requirements)
