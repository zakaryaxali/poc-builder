"""Design system data models and validation."""

from pydantic import BaseModel, Field


class ColorPalette(BaseModel):
    """Color definitions for the design system."""

    # Primary colors
    primary: str = Field(..., description="Primary brand color (hex)")
    primary_hover: str = Field(..., description="Primary hover state color (hex)")
    primary_light: str = Field(..., description="Light variant of primary (hex)")
    primary_dark: str = Field(..., description="Dark variant of primary (hex)")

    # Secondary colors
    secondary: str = Field(..., description="Secondary brand color (hex)")
    secondary_hover: str = Field(..., description="Secondary hover state color (hex)")

    # Neutral colors
    background: str = Field(default="#ffffff", description="Main background color")
    surface: str = Field(default="#ffffff", description="Surface/card background color")
    border: str = Field(default="#e5e7eb", description="Border color")
    divider: str = Field(default="#e1e1e1", description="Divider line color")

    # Text colors
    text_heading: str = Field(default="#333333", description="Heading text color")
    text_body: str = Field(default="#262626", description="Body text color")
    text_muted: str = Field(default="#555555", description="Muted/secondary text color")
    text_disabled: str = Field(default="#bbbcbd", description="Disabled text color")

    # Semantic colors
    success: str = Field(default="#126836", description="Success state color")
    error: str = Field(default="#e01e00", description="Error/danger state color")
    warning: str = Field(default="#f28200", description="Warning state color")
    info: str = Field(default="#041295", description="Info state color")


class Typography(BaseModel):
    """Typography system configuration."""

    # Font families
    font_family_heading: str = Field(
        default="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        description="Heading font family",
    )
    font_family_body: str = Field(
        default="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        description="Body font family",
    )
    font_family_mono: str = Field(
        default="'Monaco', 'Courier New', monospace", description="Monospace font family"
    )

    # Heading sizes
    font_size_h1: str = Field(default="48px", description="H1 font size")
    font_size_h2: str = Field(default="36px", description="H2 font size")
    font_size_h3: str = Field(default="28px", description="H3 font size")
    font_size_h4: str = Field(default="24px", description="H4 font size")
    font_size_h5: str = Field(default="20px", description="H5 font size")
    font_size_h6: str = Field(default="18px", description="H6 font size")

    # Body sizes
    font_size_body_large: str = Field(default="18px", description="Large body text")
    font_size_body: str = Field(default="16px", description="Standard body text")
    font_size_body_small: str = Field(default="14px", description="Small body text")
    font_size_caption: str = Field(default="12px", description="Caption text")

    # Font weights
    font_weight_light: int = Field(default=300, description="Light font weight")
    font_weight_regular: int = Field(default=400, description="Regular font weight")
    font_weight_medium: int = Field(default=500, description="Medium font weight")
    font_weight_semibold: int = Field(default=600, description="Semibold font weight")
    font_weight_bold: int = Field(default=700, description="Bold font weight")

    # Line heights
    line_height_tight: float = Field(default=1.25, description="Tight line height")
    line_height_normal: float = Field(default=1.5, description="Normal line height")
    line_height_relaxed: float = Field(default=1.75, description="Relaxed line height")

    # Letter spacing
    letter_spacing_tight: str = Field(default="-0.02em", description="Tight letter spacing")
    letter_spacing_normal: str = Field(default="0", description="Normal letter spacing")
    letter_spacing_wide: str = Field(default="0.05em", description="Wide letter spacing")


class Spacing(BaseModel):
    """Spacing scale for margins and padding."""

    xs: str = Field(default="4px", description="4px")
    sm: str = Field(default="8px", description="8px")
    md: str = Field(default="16px", description="16px")
    lg: str = Field(default="24px", description="24px")
    xl: str = Field(default="32px", description="32px")
    xxl: str = Field(default="48px", description="48px - 2xl")
    xxxl: str = Field(default="64px", description="64px - 3xl")


class BorderWidth(BaseModel):
    """Border width values."""

    thin: str = Field(default="1px", description="Thin border")
    medium: str = Field(default="2px", description="Medium border")
    thick: str = Field(default="4px", description="Thick border")


class BorderRadius(BaseModel):
    """Border radius values."""

    none: str = Field(default="0px", description="No rounding")
    sm: str = Field(default="4px", description="Small rounding")
    md: str = Field(default="8px", description="Medium rounding")
    lg: str = Field(default="16px", description="Large rounding")
    xl: str = Field(default="24px", description="Extra large rounding")
    full: str = Field(default="9999px", description="Fully rounded (pills)")


class Shadow(BaseModel):
    """Box shadow definitions."""

    none: str = Field(default="none", description="No shadow")
    sm: str = Field(default="0 1px 2px rgba(0,0,0,0.05)", description="Small shadow")
    md: str = Field(default="0 4px 6px rgba(0,0,0,0.1)", description="Medium shadow")
    lg: str = Field(default="0 10px 15px rgba(0,0,0,0.1)", description="Large shadow")
    xl: str = Field(default="0 20px 25px rgba(0,0,0,0.15)", description="Extra large shadow")


class Animation(BaseModel):
    """Animation and transition settings."""

    duration_fast: str = Field(default="150ms", description="Fast animation duration")
    duration_normal: str = Field(default="300ms", description="Normal animation duration")
    easing: str = Field(default="ease", description="Transition easing function")


class Layout(BaseModel):
    """Layout and container settings."""

    max_width: str = Field(default="1368px", description="Maximum container width")
    section_padding_vertical: str = Field(default="80px", description="Section vertical padding")
    section_padding_horizontal: str = Field(default="24px", description="Section horizontal padding")
    grid_gap: str = Field(default="24px", description="Grid gap spacing")


class Breakpoints(BaseModel):
    """Responsive design breakpoints."""

    sm: str = Field(default="640px", description="Small devices")
    md: str = Field(default="768px", description="Medium devices")
    lg: str = Field(default="1024px", description="Large devices")
    xl: str = Field(default="1280px", description="Extra large devices")


class DesignSystem(BaseModel):
    """Complete design system configuration."""

    name: str = Field(..., description="Design system name")
    colors: ColorPalette
    typography: Typography = Field(default_factory=Typography)
    spacing: Spacing = Field(default_factory=Spacing)
    border_width: BorderWidth = Field(default_factory=BorderWidth)
    border_radius: BorderRadius = Field(default_factory=BorderRadius)
    shadows: Shadow = Field(default_factory=Shadow)
    animation: Animation = Field(default_factory=Animation)
    layout: Layout = Field(default_factory=Layout)
    breakpoints: Breakpoints = Field(default_factory=Breakpoints)
