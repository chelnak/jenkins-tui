from __future__ import annotations

from rich import box
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widgets import Button, ButtonPressed

from .. import styles
from ..renderables import ButtonRenderable


class ButtonWidget(Button):

    mouse_over: bool = Reactive(False)
    toggle: bool = Reactive(False)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def render(self) -> RenderableType:
        assert isinstance(self.label, Text)
        text_style = Style(underline=self.toggle)
        border_style = Style(
            color=styles.GREY, bold=True, dim=self.mouse_over or self.toggle
        )
        box_style = box.DOUBLE if self.toggle else box.SQUARE
        self.label.stylize(style=text_style)
        panel_content = ButtonRenderable(self.label)
        return Panel(
            panel_content, box=box_style, border_style=border_style, expand=False
        )

    async def on_click(self, event: events.Click) -> None:
        self.toggle = False if self.toggle else True
        event.prevent_default().stop()
        await self.emit(ButtonPressed(self))
