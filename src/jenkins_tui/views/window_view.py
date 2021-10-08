from __future__ import annotations
from typing import Optional, cast

from textual import events
from textual.geometry import Size
from textual.layouts.dock import Dock, DockEdge, DockLayout
from textual.view import View
from textual import messages
from textual.widget import Widget

from textual.views._window_view import WindowChange


class DoNotSet:
    pass


do_not_set = DoNotSet()


class WindowView(View):
    """A copy of textual.views.WindowView that implements docking. This will be refactored in the future."""

    def __init__(self) -> None:
        name = self.__class__.__name__
        super().__init__(layout=DockLayout(), name=name)

    async def dock(
        self,
        *widgets: Widget,
        edge: DockEdge = "top",
        z: int = 0,
        size: int | None | DoNotSet = do_not_set,
        name: str | None = None
    ) -> None:

        dock = Dock(edge, widgets, z)
        assert isinstance(self.layout, DockLayout)
        self.layout.docks.append(dock)

        for widget in widgets:
            if size is not do_not_set:
                widget.layout_size = cast(Optional[int], size)
            if name is None:
                await self.mount(widget)
            else:
                await self.mount(**{name: widget})
        await self.refresh_layout()

    async def update(
        self,
        *widgets: Widget,
        edge: DockEdge = "top",
        z: int = 0,
        size: int | None | DoNotSet = do_not_set,
        name: str | None = None
    ) -> None:

        assert isinstance(self.layout, DockLayout)
        self.layout.docks.clear()

        dock = Dock(edge, widgets, z)
        self.layout.docks.append(dock)

        for widget in widgets:
            if size is not do_not_set:
                widget.layout_size = cast(Optional[int], size)
            if name is None:
                await self.mount(widget)
            else:
                await self.mount(**{name: widget})

        self.layout.require_update()
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
