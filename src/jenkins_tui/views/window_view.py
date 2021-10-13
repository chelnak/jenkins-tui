from __future__ import annotations
from typing import List

from textual import events
from textual import messages
from textual.geometry import Size, SpacingDimensions
from textual.widget import Widget

from textual.view import View
from textual.layouts.vertical import VerticalLayout
from textual.views._window_view import WindowChange

from rich.console import RenderableType


class DoNotSet:
    pass


do_not_set = DoNotSet()


class WindowView(View):
    def __init__(
        self,
        widgets: List[RenderableType | Widget],
        *,
        auto_width: bool = False,
        gutter: SpacingDimensions = (1, 0),
        name: str | None = None
    ) -> None:
        layout = VerticalLayout(gutter=gutter, auto_width=auto_width)
        for widget in widgets:
            layout.add(widget)
        super().__init__(name=name, layout=layout)

    async def update(self, widgets: List[RenderableType | Widget]) -> None:
        layout = self.layout
        assert isinstance(layout, VerticalLayout)
        layout.clear()

        for widget in widgets:
            layout.add(widget)

        await self.refresh_layout()
        await self.emit(WindowChange(self))

    async def handle_update(self, message: messages.Update) -> None:
        message.prevent_default()
        await self.emit(WindowChange(self))

    async def handle_layout(self, message: messages.Layout) -> None:
        self.log("TRANSLATING layout")
        self.layout.require_update()
        message.stop()
        self.refresh()

    async def watch_virtual_size(self, size: Size) -> None:
        await self.emit(WindowChange(self))

    async def watch_scroll_x(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def watch_scroll_y(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        await self.emit(WindowChange(self))
