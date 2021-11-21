from pyfiglet import Figlet
from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text


class FigletTextRenderable:
    """A renderable to generate figlet text that adapts to fit the container.
    The class originates from here: https://github.com/willmcgugan/textual/blob/f47b3e089c681275c48c0debc7a320b66a772a50/examples/calculator.py#L27
    """

    def __init__(self, text: str) -> None:
        self.text = text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Build a Rich renderable to render the Figlet text."""
        size = min(options.max_width / 2, options.max_height)
        if size < 4:
            yield Text(self.text, style="bold")
        else:
            if size < 7:
                font_name = "mini"
            elif size < 8:
                font_name = "small"
            elif size < 10:
                font_name = "standard"
            else:
                font_name = "big"
            font = Figlet(font=font_name, width=options.max_width)
            yield Text(font.renderText(self.text).rstrip("\n"), style="bold")
