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
from ..renderables import BuildHistoryTableRenderable


class JobDetailsWidget(Widget):
    """A job details widget. Used to display builds within a job."""

    page: int = 1
    row: int = 0

    @inject
    def __init__(
        self, job: dict[str, Any], client: Jenkins = Provide[Container.client]
    ) -> None:
        """A job details widget. Used to display builds within a job.

        Args:
            job (dict[str, Any]): A dict of job info.

        # noqa: DAR101 client
        """

        name = self.__class__.__name__
        super().__init__(name=name)
        self.job = job
        self.client = client
        self.builds: list[dict[str, Any]] = []
        self.renderable: BuildHistoryTableRenderable | None = None

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        await self.app.set_focus(self)

    async def update(self, job: dict[str, Any]) -> None:
        """Updates the widget with new job info.

        Args:
            job (dict[str, Any]): A dict of job info.
        """

        self.job = job
        self.refresh(layout=True)

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

    def render_history_table(self) -> None:
        """Renders the build history table."""

        self.builds = self.job.get("builds", [])
        self.renderable = BuildHistoryTableRenderable(
            builds=self.builds,
            title="history",
            page_size=self.size.height - 5,
            page=self.page,
            row=self.row,
        )

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

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
