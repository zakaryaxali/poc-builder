"""Design system data models and validation."""

from pydantic import BaseModel, Field


class ColorPalette(BaseModel):
    """Color definitions for the design system.

    This model accepts any color tokens as a flexible dict to support
    the full Quantum color system (blue_50-900, bluegrey_25-900, etc.)
    """

    class Config:
        extra = "allow"  # Allow any additional color tokens

    def __getitem__(self, key: str) -> str:
        """Allow dict-like access for template rendering."""
        return getattr(self, key, None)

    def __iter__(self):
        """Allow iteration over color tokens."""
        return iter(self.__dict__.items())


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
    duration_slow: str = Field(default="500ms", description="Slow animation duration")
    easing: str = Field(
        default="cubic-bezier(0.4, 0, 0.2, 1)", description="Transition easing function"
    )


class Layout(BaseModel):
    """Layout and container settings."""

    max_width: str = Field(default="1368px", description="Maximum container width")
    section_padding_vertical: str = Field(default="80px", description="Section vertical padding")
    section_padding_horizontal: str = Field(default="24px", description="Section horizontal padding")
    grid_gap: str = Field(default="24px", description="Grid gap spacing")
    container_padding: str = Field(default="24px", description="Container padding")


class SemanticColors(BaseModel):
    """Semantic color tokens for specific UI states."""

    class Config:
        extra = "allow"  # Allow any additional semantic color tokens

    primary_default: str = Field(default="#041295", description="Primary color")
    primary_hover: str = Field(default="#020B59", description="Primary hover color")
    neutral_default: str = Field(default="#383A4B", description="Neutral color")
    success_default: str = Field(default="#178244", description="Success color")
    success_bg: str = Field(default="#E8F3ED", description="Success background")
    success_text: str = Field(default="#0E4E29", description="Success text")
    warning_default: str = Field(default="#E07900", description="Warning color")
    warning_bg: str = Field(default="#FCF2E6", description="Warning background")
    warning_text: str = Field(default="#864900", description="Warning text")
    danger_default: str = Field(default="#E01E00", description="Danger color")
    danger_bg: str = Field(default="#FCE9E6", description="Danger background")
    danger_text: str = Field(default="#861200", description="Danger text")
    info_default: str = Field(default="#041295", description="Info color")
    info_bg: str = Field(default="#E6E7F4", description="Info background")
    info_text: str = Field(default="#020B59", description="Info text")
    focused: str = Field(default="#6871BF", description="Focus ring color")


class HeaderTokens(BaseModel):
    """Header component tokens."""

    class Config:
        extra = "allow"

    height: str = Field(default="64px", description="Header height")
    background: str = Field(default="#FFFFFF", description="Header background")
    border_bottom_color: str = Field(default="#BCBECE", description="Header border color")
    border_bottom_width: str = Field(default="1px", description="Header border width")
    logo_height: str = Field(default="24px", description="Logo height")
    padding_horizontal: str = Field(default="24px", description="Horizontal padding")
    item_gap: str = Field(default="8px", description="Gap between header items")
    nav_item_padding: str = Field(default="16px 20px", description="Navigation item padding")


class ButtonTokens(BaseModel):
    """Button component tokens."""

    class Config:
        extra = "allow"

    padding_sm: str = Field(default="6px 12px", description="Small button padding")
    padding_md: str = Field(default="10px 20px", description="Medium button padding")
    padding_lg: str = Field(default="14px 24px", description="Large button padding")
    border_radius: str = Field(default="8px", description="Button border radius")
    font_size_sm: str = Field(default="14px", description="Small button font size")
    font_size_md: str = Field(default="16px", description="Medium button font size")
    font_size_lg: str = Field(default="18px", description="Large button font size")
    font_weight: int = Field(default=500, description="Button font weight")
    primary_bg: str = Field(default="#041295", description="Primary button background")
    primary_bg_hover: str = Field(default="#020B59", description="Primary button hover background")
    primary_text: str = Field(default="#FFFFFF", description="Primary button text")
    secondary_bg: str = Field(default="transparent", description="Secondary button background")
    secondary_border: str = Field(default="#041295", description="Secondary button border")
    secondary_text: str = Field(default="#041295", description="Secondary button text")
    secondary_bg_hover: str = Field(default="#F7F7F9", description="Secondary button hover")
    danger_bg: str = Field(default="#E01E00", description="Danger button background")
    danger_bg_hover: str = Field(default="#B31800", description="Danger button hover background")
    danger_text: str = Field(default="#FFFFFF", description="Danger button text")


class CardTokens(BaseModel):
    """Card component tokens."""

    class Config:
        extra = "allow"

    background: str = Field(default="#FFFFFF", description="Card background")
    border_radius: str = Field(default="16px", description="Card border radius")
    padding: str = Field(default="24px", description="Card padding")
    shadow: str = Field(default="0 4px 6px rgba(0,0,0,0.1)", description="Card shadow")
    border_color: str = Field(default="#BCBECE", description="Card border color")
    border_width: str = Field(default="0px", description="Card border width")


class BadgeTokens(BaseModel):
    """Badge component tokens."""

    class Config:
        extra = "allow"

    padding: str = Field(default="4px 12px", description="Badge padding")
    border_radius: str = Field(default="9999px", description="Badge border radius")
    font_size: str = Field(default="12px", description="Badge font size")
    font_weight: int = Field(default=500, description="Badge font weight")
    success_bg: str = Field(default="#E8F3ED", description="Success badge background")
    success_text: str = Field(default="#0E4E29", description="Success badge text")
    warning_bg: str = Field(default="#FCF2E6", description="Warning badge background")
    warning_text: str = Field(default="#864900", description="Warning badge text")
    danger_bg: str = Field(default="#FCE9E6", description="Danger badge background")
    danger_text: str = Field(default="#861200", description="Danger badge text")
    info_bg: str = Field(default="#E6E7F4", description="Info badge background")
    info_text: str = Field(default="#020B59", description="Info badge text")
    neutral_bg: str = Field(default="#EEEFF3", description="Neutral badge background")
    neutral_text: str = Field(default="#383A4B", description="Neutral badge text")


class InputTokens(BaseModel):
    """Input component tokens."""

    class Config:
        extra = "allow"

    padding: str = Field(default="10px 12px", description="Input padding")
    border_radius: str = Field(default="8px", description="Input border radius")
    border_width: str = Field(default="1px", description="Input border width")
    border_color: str = Field(default="#BCBECE", description="Input border color")
    border_color_hover: str = Field(default="#9A9DB5", description="Input border hover color")
    border_color_focus: str = Field(default="#041295", description="Input border focus color")
    border_color_error: str = Field(default="#E01E00", description="Input border error color")
    background: str = Field(default="#FFFFFF", description="Input background")
    background_disabled: str = Field(default="#F7F7F9", description="Input disabled background")
    text_color: str = Field(default="#131319", description="Input text color")
    text_color_disabled: str = Field(default="#9A9DB5", description="Input disabled text color")
    placeholder_color: str = Field(default="#5D607E", description="Input placeholder color")
    focus_ring_color: str = Field(default="#6871BF", description="Input focus ring color")
    focus_ring_width: str = Field(default="2px", description="Input focus ring width")
    focus_ring_offset: str = Field(default="2px", description="Input focus ring offset")


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
    semantic_colors: SemanticColors = Field(default_factory=SemanticColors)
    typography: Typography = Field(default_factory=Typography)
    spacing: Spacing = Field(default_factory=Spacing)
    border_width: BorderWidth = Field(default_factory=BorderWidth)
    border_radius: BorderRadius = Field(default_factory=BorderRadius)
    shadows: Shadow = Field(default_factory=Shadow)
    animation: Animation = Field(default_factory=Animation)
    layout: Layout = Field(default_factory=Layout)
    breakpoints: Breakpoints = Field(default_factory=Breakpoints)
    header: HeaderTokens = Field(default_factory=HeaderTokens)
    button: ButtonTokens = Field(default_factory=ButtonTokens)
    card: CardTokens = Field(default_factory=CardTokens)
    badge: BadgeTokens = Field(default_factory=BadgeTokens)
    input: InputTokens = Field(default_factory=InputTokens)
