from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.style import StyleType


class ButtonRenderable:
    """A button renderable."""

    def __init__(self, label: RenderableType, style: StyleType = "") -> None:
        """A button renderable.

        Args:
            label (RenderableType): The text to display.
            style (StyleType, optional): A style object. Defaults to "".
        """
        self.label = label
        self.style = style

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        height = options.height or 1

        yield Align.center(
            self.label, vertical="middle", style=self.style, width=width, height=height
        )
