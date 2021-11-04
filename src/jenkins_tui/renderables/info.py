from __future__ import annotations

from __future__ import annotations
from typing import Optional

from rich.text import Text
from rich.console import Group, RenderResult, RenderableType, Console, ConsoleOptions
from rich.padding import Padding
from rich.text import Text
from rich.rule import Rule


class InfoRenderable:
    """An info renderable."""

    def __init__(
        self, title: str, renderable: Optional[str | Text | RenderableType] = None
    ) -> None:
        """An info renderable.

        Args:
            title (str): The title to display.
            renderable (Optional[str, optional): A renderable that will be displayed in the main body of a widget.. Defaults to None.
        """
        self.title = title
        self.renderable = renderable

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        title = Rule(Text(self.title, style="bold"), style="grey82")
        renderable = Padding("")

        if self.renderable:
            renderable = Padding(
                renderable=self.renderable,
                pad=(1, 0, 0, 0),
            )

        yield Padding(
            Group(title, renderable),
            pad=(0, 0, 0, 0),
        )
