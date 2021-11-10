from __future__ import annotations

from typing import Any, Optional

from rich.console import RenderableType
from rich.text import Text
from rich.panel import Panel

from textual.widget import Widget
from textual.reactive import Reactive
from textual.keys import Keys
from textual import events

from ..renderables import (
    PaginatedTableRenderable,
    BuildHistoryTableRenderable,
    BuildChangesTableRenderable,
)


class JobDetailsWidget(Widget):
    """A build table widget. Used to display builds within a job."""

    table: Optional[PaginatedTableRenderable] = None
    title: Reactive[str] = Reactive("")

    def __init__(self, job: dict[str, Any]) -> None:
        """A build table widget.

        Args:
            job (dict[str, Any]): A dict of job info.
        """

        self.job = job
        name = self.__class__.__name__
        super().__init__(name=name)

    def on_key(self, event: events.Key) -> None:
        if self.table is None:
            return

        key = event.key
        if key == Keys.Left:
            self.table.previous_page()
        elif key == Keys.Right:
            self.table.next_page()
        elif key == "f":
            self.table.first_page()
        elif key == "l":
            self.table.last_page()
        elif key == Keys.Up:
            self.table.previous_row()
        elif key == Keys.Down:
            self.table.next_row()

        self.refresh()

    async def on_mount(self) -> None:
        """Overrides on_mount from textual.widget.Widget"""
        if not self.table:
            self.render_history_table()

        self.refresh(layout=True)

    def render_history_table(self) -> None:
        """Renders the build history table."""
        builds = self.job.get("builds")
        self.table = BuildHistoryTableRenderable(
            builds if builds else [],
            page_size=self.size.height - 5,
            page=self.table.page if self.table else 1,
            row=self.table.row if self.table else 0,
        )

        self.title = "history"

    def render_changes_table(self) -> None:

        builds = self.job.get("builds")
        self.table = BuildChangesTableRenderable(
            builds if builds else [],
            page_size=self.size.height - 5,
            page=self.table.page if self.table else 1,
            row=self.table.row if self.table else 0,
        )
        self.title = "changes"

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        if not self.table:
            self.render_history_table()

        assert isinstance(self.table, PaginatedTableRenderable)
        body = Panel(
            renderable=self.table,
            title=Text.from_markup(f"[bold]{self.title}[/]"),
            border_style="grey82",
            title_align="center",
            expand=True,
        )
        return body
