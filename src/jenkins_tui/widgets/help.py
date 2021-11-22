from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from textual.widget import Widget

from .. import styles
from ..renderables import HelpRenderable


class HelpWidget(Widget):
    def render(self) -> RenderableType:
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
