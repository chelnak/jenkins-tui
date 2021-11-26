from __future__ import annotations

from typing import Any

from dependency_injector.wiring import Provide, inject
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from textual import events
from textual.keys import Keys
from textual.widget import Widget

from .. import styles
from ..containers import Container
from ..jenkins import Jenkins
from ..renderables import ExecutorStatusTableRenderable


class ExecutorStatusWidget(Widget):
    """An executor status widget. Used to display running builds on the server."""

    page: int = 1
    row: int = 0

    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]) -> None:
        """An executor status widget. Used to display running builds on the server.

        # noqa: DAR101 client
        """

        name = self.__class__.__name__
        super().__init__(name=name)
        self.client = client
        self.running_builds: list[dict[str, Any]] = []
        self.queued_builds: list[dict[str, Any]] = []
        self.running_builds_count: int = 0
        self.queued_builds_count: int = 0
        self.renderable: ExecutorStatusTableRenderable | None = None

    def on_key(self, event: events.Key) -> None:
        """Handle a key press.

        Args:
            event (events.Key): The event containing the pressed key.
        """

        if self.renderable is None:
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
            page=self.page,
            row=self.row,
        )

    async def _update(self) -> None:
        """Update the current renderable object."""

        self.running_builds = await self.client.get_running_builds()
        self.queued_builds = await self.client.get_queued_jobs()
        self.running_builds_count = len(self.running_builds)
        self.queued_builds_count = len(self.queued_builds)

        self.refresh(layout=True)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        await self._update()
        self.render_executor_status_table()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        if self.renderable is not None:
            self.page = self.renderable.page

        self.render_executor_status_table()

        assert isinstance(self.renderable, ExecutorStatusTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[{styles.GREY}](queued: [{styles.ORANGE}]{self.queued_builds_count}[/] / running [green]{self.running_builds_count}[/])[/]",
            border_style=Style(color=styles.PURPLE),
            padding=(1),
            expand=True,
            box=styles.BOX,
        )
