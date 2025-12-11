"""Design system loading utilities.

POC Builder uses the Quantum design system by default.
All generated projects will follow the Quantum brand guidelines.
"""

import json
from pathlib import Path

from src.design_system.models import DesignSystem


def load_design_system(path: str | Path) -> DesignSystem:
    """Load and validate a design system from a JSON file.

    Args:
        path: Path to the design system JSON file

    Returns:
        Validated DesignSystem instance

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the JSON is invalid or doesn't match the schema
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Design system file not found: {path}")

    with open(file_path) as f:
        data = json.load(f)

    try:
        return DesignSystem(**data)
    except Exception as e:
        raise ValueError(f"Invalid design system configuration: {e}") from e


def get_default_design_system() -> DesignSystem:
    """Load the Quantum design system.

    Returns:
        Quantum DesignSystem instance with brand colors, typography, and styling
    """
    default_path = Path(__file__).parent.parent.parent / "design_systems" / "default.json"
    return load_design_system(default_path)
