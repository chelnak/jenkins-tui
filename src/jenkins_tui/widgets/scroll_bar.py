from rich.color import Color
from rich.console import RenderableType
from rich.style import Style
from textual.scrollbar import ScrollBar, ScrollBarRender


class ScrollBarWidget(ScrollBar):
    """A custom scrollbar widget"""

    def render(self) -> RenderableType:
        """Overrides render from textual.scrollbar.ScrollBar"""

        style = Style(
            bgcolor=Color.parse("#444444"),
            color=Color.parse("#9c9a9a" if self.grabbed else "#6e6d6d"),
        )

        return ScrollBarRender(
            virtual_size=self.virtual_size,
            window_size=self.window_size,
            position=self.position,
            vertical=self.vertical,
            style=style,
        )
