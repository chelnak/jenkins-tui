from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from textual.widget import Widget

from .. import styles
from ..renderables import HelpRenderable


class HelpWidget(Widget):
    """A custom help widget."""

    def __init__(self) -> None:
        """A custom help widget."""

        super().__init__()
        self.visible = False

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        top_padding = 1
        _, height = self.size
        return Padding(
            Panel(
                HelpRenderable(),
                title="❔ [bold]help[/]",
                border_style=styles.PURPLE,
                box=styles.BOX,
                title_align="left",
                padding=(1, 0, 0, 0),
                height=height - top_padding,
            ),
            pad=(top_padding, 0, 0, 0),
        )
