from __future__ import annotations

from typing import Any, Optional
from dependency_injector.wiring import Provide, inject

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from rich.panel import Panel

from textual.widget import Widget
from textual.keys import Keys
from textual import events

from ..client import Jenkins
from ..containers import Container
from ..renderables import (
    BuildHistoryTableRenderable,
)


class JobDetailsWidget(Widget):
    """A build table widget. Used to display builds within a job."""

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
        self.job: dict[str, Any] = {}
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
            builds=self.job.get("builds", []),
            title="history",
            page_size=self.size.height - 5,
            page=self.renderable.page if self.renderable else 1,
            row=self.renderable.row if self.renderable else 0,
        )

    async def _update(self) -> None:
        """Update the current renderable object."""
        self.job = await self.client.get_job(path=self.path)
        self.refresh(layout=True)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        await self._update()
        self.render_history_table()
        self.set_interval(20, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""
        self.render_history_table()
        assert isinstance(self.renderable, BuildHistoryTableRenderable)
        return Panel(
            renderable=self.renderable,
            title=Text.from_markup(f"[grey82]( {self.renderable.title} )[/]"),
            border_style=Style(color="medium_purple4"),
            title_align="center",
            expand=True,
        )
