from __future__ import annotations

from typing import Optional

from rich.align import Align
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style
from rich.text import Text


class TextRenderable:
    """An text renderable."""

    def __init__(
        self,
        text: Optional[str | Text | RenderableType] = None,
    ) -> None:
        """A text renderable.

        Args:
            renderable (optional, str, Text, RenderableType): A renderable that will be displayed in the main body of a widget.
        """
        self.text = text or ""

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        yield Padding(self.text, pad=(0, 1, 0, 1))
