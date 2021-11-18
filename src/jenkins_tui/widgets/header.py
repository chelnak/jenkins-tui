from __future__ import annotations

from typing import Optional

from rich import box, style
from rich.align import Align
from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.reactive import Reactive
from textual.widget import Widget

from ..renderables import FigletTextRenderable


class HeaderWidget(Widget):
    """A generic info widget. This displays information with a ruled title and some text"""

    title: Reactive[str | Text] = Reactive("Welcome!")

    def __init__(
        self,
    ) -> None:
        """A generic info widget. This displays information with a ruled title and some text.

        Args:
            title (str, optional): The title of the info widget. Defaults to None.
            renderable (str, Text, optional): The text that will be rendered in the info widget. Defaults to None.
        """

        name = self.__class__.__name__
        super().__init__(name=name)
        self.layout_size = 8

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        header = Table(
            show_header=False,
            show_lines=False,
            box=box.ROUNDED,
            padding=(0),
            expand=True,
            border_style="medium_purple4",
        )
        header.add_column(ratio=13)
        header.add_column(ratio=60, justify="center")
        header.add_row(
            Padding(FigletTextRenderable(text="Jenkins"), style="green"),
            Padding(
                Align.center(
                    Text(
                        self.title,
                        style=Style(color="grey82", bold=True),
                    ),
                    vertical="middle",
                ),
            ),
            end_section=False,
        )

        return header
