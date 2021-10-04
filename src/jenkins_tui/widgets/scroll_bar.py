from .. import config

from rich.color import Color
from rich.console import RenderableType
from rich.style import Style
from textual.scrollbar import ScrollBar as TextualScrollBar, ScrollBarRender


class ScrollBar(TextualScrollBar):
    """A custom scrollbar widget"""

    def __init__(self, **kwargs):
        """A custom textual.scrollbar.ScrollBar implementation that enabled styling."""
        super().__init__(**kwargs)

    def render(self) -> RenderableType:
        """Overrides render from textual.scrollbar.ScrollBar"""

        _styles = config.style_map[config.style]

        style = Style(
            bgcolor=(
                Color.parse(
                    _styles["scroll_bar_background_on_hover"]
                    if self.mouse_over
                    else _styles["scroll_bar_background"]
                )
            ),
            color=Color.parse(
                _styles["scroll_bar_grabbed_foreground"]
                if self.grabbed
                else _styles["scroll_bar_foreground"]
            ),
        )

        return ScrollBarRender(
            virtual_size=self.virtual_size,
            window_size=self.window_size,
            position=self.position,
            vertical=self.vertical,
            style=style,
        )
