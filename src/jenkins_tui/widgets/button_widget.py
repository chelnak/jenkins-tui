from re import S
from rich import box
from rich.style import StyleType
from rich.console import Console, ConsoleOptions, RenderResult
from rich.align import Align
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events

from textual.reactive import Reactive
from textual.widgets import Button, ButtonPressed


class JenkinsButtonRenderable:
    def __init__(self, label: RenderableType, style: StyleType = "") -> None:
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


class JenkinsButton(Button):

    mouse_over: bool = Reactive(False)
    toggle: bool = Reactive(False)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def render(self) -> RenderableType:
        assert isinstance(self.label, Text)
        text_style = Style(underline=self.toggle)
        border_style = Style(color="green", dim=self.mouse_over or self.toggle)

        self.label.stylize(style=text_style)
        panel_content = JenkinsButtonRenderable(self.label)
        return Panel(
            panel_content, box=box.SQUARE, border_style=border_style, expand=True
        )

    async def on_click(self, event: events.Click) -> None:

        self.toggle = False if self.toggle else True

        event.prevent_default().stop()
        await self.emit(ButtonPressed(self))
