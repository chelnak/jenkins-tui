from __future__ import annotations

from .base import BaseView


class JobNavView(BaseView):
    """A view that contains widgets that make up the job navigation."""

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        await self.add_button(text="history (h)", id="history")
        # await self.add_button(text="changes (c)", id="changes")
        await self.add_button(text="build (b)", id="build")

        for k, _ in self.buttons.items():
            self.layout.add_column(f"col_{k}", size=15)

        self.layout.add_row("row", size=3)
        self.layout.set_align("center", "center")
        self.layout.set_gutter(0, 0)

        # we always land on history so toggle the button
        self.buttons["history"].toggle = True
        self.parent.current_button = self.buttons["history"]

        self.layout.place(*list(self.buttons.values()))
