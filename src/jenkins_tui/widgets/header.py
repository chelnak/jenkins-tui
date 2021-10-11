from rich.console import RenderableType
from rich.style import StyleType
from rich.table import Table
from rich.panel import Panel
from textual.widget import Widget

from textual.reactive import Reactive
from .. import config


class Header(Widget):
    """A custom header widget"""

    style: Reactive[StyleType] = Reactive("")
    layout_size: Reactive[int] = 3

    def render(self) -> RenderableType:

        self.style = ""
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_row(config.app_name)
        header: RenderableType
        header = Panel(header_table)
        return header
