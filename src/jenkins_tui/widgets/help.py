from rich import box
from rich.panel import Panel
from textual.widget import Widget

from ..renderables import HelpRenderable


class HelpWidget(Widget):
    def render(self) -> Panel:
        return Panel(
            HelpRenderable(),
            title="❔ [bold]help[/]",
            border_style="medium_purple4",
            box=box.HEAVY_EDGE,
            title_align="left",
            padding=(1, 0, 0, 0),
        )
