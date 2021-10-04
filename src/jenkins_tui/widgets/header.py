from rich.console import RenderableType
from rich.style import StyleType
from rich.table import Table
from rich.panel import Panel

from textual.widgets import Header as TextualHeader
from textual.reactive import Reactive


class Header(TextualHeader):
    """A custom header widget"""

    style: Reactive[StyleType] = Reactive("")
    layout_size: Reactive[int] = 3
    tall: Reactive[bool] = False

    def render(self) -> RenderableType:
        """Overrides render from textual.widgets.Header"""

        self.style = ""
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_row(self.title)
        header: RenderableType
        header = Panel(header_table)
        return header

    async def watch_tall(self, tall: bool) -> None:
        """Overrides watch_tall from textual.widgets.Header to disable header resizing on click."""
        pass
