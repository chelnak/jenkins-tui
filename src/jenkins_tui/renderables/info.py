from __future__ import annotations

from typing import Optional

from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.text import Text


class InfoRenderable:
    """An info renderable."""

    def __init__(
        self,
        title: str | Text | RenderableType,
        renderable: Optional[str | Text | RenderableType],
    ) -> None:
        """An info renderable.

        Args:
            title (str, Text, RenderableType): The title to display.
            renderable (optional, str, Text, RenderableType): A renderable that will be displayed in the main body of a widget.
        """
        self.title = title
        self.renderable = renderable

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        title = Panel(
            Align.center(
                renderable=Text(
                    self.title,
                    style=Style(color="grey82", bold=True),
                )
                if isinstance(self.title, str)
                else self.title,
                vertical="middle",
            ),
            height=6,
            border_style=Style(color="medium_purple4"),
            padding=(0, 0, 0, 0),
        )

        if not self.renderable:
            group = Group(title)
        else:
            renderable = Padding(renderable=self.renderable, pad=(1))
            group = Group(title, renderable)

        yield Padding(group, pad=(1, 0, 0, 0))
