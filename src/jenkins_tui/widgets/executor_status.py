from __future__ import annotations

from typing import Any, Optional
from dependency_injector.wiring import inject, Provide


from rich.console import RenderableType
from rich.panel import Panel
from rich.align import Align
from rich.style import Style

from textual import events
from textual.keys import Keys
from textual.widget import Widget

from ..client import Jenkins
from ..containers import Container
from ..renderables import ExecutorStatusTableRenderable


class ExecutorStatusWidget(Widget):
    """An executor status widget. Used to display running builds on the server."""

    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]) -> None:
        """An executor status widget.

        Args:
            client (Jenkins): An instance of Jenkins
        """
        self.client = client
        name = self.__class__.__name__
        super().__init__(name=name)

        self.running_builds: list[dict[str, Any]] = []
        self.queued_builds: list[dict[str, Any]] = []
        self.running_builds_count: int = 0
        self.queued_builds_count: int = 0
        self.renderable: Optional[ExecutorStatusTableRenderable] = None

    def on_key(self, event: events.Key) -> None:
        if self.renderable is None:
            return

        if isinstance(self.renderable, Align):
            return

        key = event.key
        if key == Keys.Left:
            self.renderable.previous_page()
        elif key == Keys.Right:
            self.renderable.next_page()
        elif key == "f":
            self.renderable.first_page()
        elif key == "l":
            self.renderable.last_page()
        elif key == Keys.Up:
            self.renderable.previous_row()
        elif key == Keys.Down:
            self.renderable.next_row()

        self.refresh()

    def render_executor_status_table(self) -> None:
        """Render the executor status table."""
        self.renderable = ExecutorStatusTableRenderable(
            builds=self.running_builds or [],
            page_size=self.size.height - 4,
            page=self.renderable.page if self.renderable else 1,
            row=self.renderable.row if self.renderable else 0,
        )

    async def _update(self):
        """Update the current renderable object."""

        self.running_builds = await self.client.get_running_builds()
        self.queued_builds = await self.client.get_queued_jobs()
        self.running_builds_count = len(self.running_builds)
        self.queued_builds_count = len(self.queued_builds)

        self.refresh(layout=True)

    async def on_mount(self):
        """Actions that are executed when the widget is mounted."""
        await self._update()
        self.render_executor_status_table()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""
        self.render_executor_status_table()
        assert isinstance(self.renderable, ExecutorStatusTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[grey82](queued: [orange3]{self.queued_builds_count}[/] / running [green]{self.running_builds_count}[/])[/]",
            expand=True,
            padding=(1),
            border_style=Style(color="medium_purple4"),
        )
