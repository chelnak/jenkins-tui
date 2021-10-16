from __future__ import annotations

from textual import messages
from textual.geometry import SpacingDimensions
from textual.view import View
from textual.layouts.grid import GridLayout
from textual.views._window_view import WindowChange


class JenkinsBaseView(View):
    """A base view containing common properties and methods."""

    def __init__(
        self,
    ) -> None:
        """A base view containing common properties and methods."""
        gutter: SpacingDimensions = (1, 0)
        name = self.__class__.__name__
        layout = GridLayout(gap=(1, 1), gutter=gutter, align=("center", "top"))
        super().__init__(name=name, layout=layout)

        self.layout: GridLayout = layout

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        pass

    async def handle_layout(self, message: messages.Layout) -> None:
        self.log("TRANSLATING layout")
        self.layout.require_update()
        message.stop()
        self.refresh()

    async def handle_update(self, message: messages.Update) -> None:
        message.prevent_default()
        await self.emit(WindowChange(self))

    async def watch_scroll_x(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def watch_scroll_y(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()
