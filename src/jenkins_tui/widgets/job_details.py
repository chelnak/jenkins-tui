from __future__ import annotations

from typing import Any, Optional

from dependency_injector.wiring import Provide, inject
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from textual import events
from textual.keys import Keys
from textual.widget import Widget

from .. import styles
from ..client import Jenkins
from ..containers import Container
from ..renderables import BuildHistoryTableRenderable


class JobDetailsWidget(Widget):
    """A build table widget. Used to display builds within a job."""

    page: int = 1
    row: int = 0

    @inject
    def __init__(self, path: str, client: Jenkins = Provide[Container.client]) -> None:
        """A build table widget.

        Args:
            job (dict[str, Any]): A dict of job info.
        """

        name = self.__class__.__name__
        super().__init__(name=name)
        self.path = path
        self.client = client
        self.builds: list[dict[str, Any]] = []
        self.renderable: Optional[BuildHistoryTableRenderable] = None

    def on_key(self, event: events.Key) -> None:
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

    def render_history_table(self) -> None:
        """Renders the build history table."""

        self.renderable = BuildHistoryTableRenderable(
            builds=self.builds,
            title="history",
            page_size=self.size.height - 5,
            page=self.page,
            row=self.row,
        )

    async def _update(self) -> None:
        """Update the current renderable object."""
        job = await self.client.get_job(path=self.path)
        self.builds = job.get("builds", [])
        self.refresh(layout=True)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        await self._update()
        self.render_history_table()
        self.set_interval(20, self._update)
        await self.app.set_focus(self)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        if self.renderable is not None:
            self.page = self.renderable.page
            self.row = self.renderable.row

        self.render_history_table()
        assert isinstance(self.renderable, BuildHistoryTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=f"[{styles.GREY}]( {self.renderable.title} )[/]",
            border_style=Style(color=styles.PURPLE),
            expand=True,
            box=styles.BOX,
        )
