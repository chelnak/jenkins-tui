from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.text import Text


class TextRenderable:
    """An text renderable."""

    def __init__(
        self,
        text: str | Text | None = None,
    ) -> None:
        """A text renderable.

        Args:
            text (str | Text | None): A renderable that will be displayed in the main body of a widget.
        """

        self.text = text or ""

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:

        yield Padding(self.text, pad=(1, 1, 0, 1))
