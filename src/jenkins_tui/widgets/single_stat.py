from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel
from rich.align import Align
from rich import box

from textual.widget import Widget
from textual.reactive import Reactive, watch

from ..renderables import FigletTextRenderable


class SingleStatWidget(Widget):
    """The digital display of the calculator."""

    value: Reactive[int] = Reactive(0)

    def __init__(self, name: str | None):
        """Initialize the calculator display."""
        super().__init__(name=name)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        watch(self, "value", self.refresh)

    def render(self) -> RenderableType:
        """Build a Rich renderable to render the calculator display."""

        return Panel(
            renderable=Align.center(
                FigletTextRenderable(str(self.value)), vertical="middle"
            ),
            box=box.DOUBLE,
            width=40,
            title=self.name,
        )
