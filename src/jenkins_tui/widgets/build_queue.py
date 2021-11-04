from datetime import datetime
from dependency_injector.wiring import Provide, inject

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box

from textual.widget import Widget

from ..client import Jenkins
from ..containers import Container


class BuildQueueWidget(Widget):
    """An build queue widget. Used to display queued builds on the server."""

    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]) -> None:
        """An build queue widget.

        Args:
            client (ExtendedJenkinsClient): An instance of ExtendedJenkinsClient.
        """
        self.client = client
        name = self.__class__.__name__
        super().__init__(name=name)

        self.renderable: RenderableType = ""

    async def _get_renderable(self):
        """Builds a renderable object."""

        queue = await self.client.get_queued_jobs()

        panel_content: RenderableType
        if len(queue) > 0:
            self.log("System has queued buids, building table.")
            table = Table(expand=True, box=box.SIMPLE)
            table.add_column(header="name", justify="left", no_wrap=True)
            table.add_column(header="reason", justify="left", no_wrap=True)
            table.add_column(header="queued since", justify="left", no_wrap=True)

            for build in queue:

                timestamp = datetime.fromtimestamp(
                    int(build["inQueueSince"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")

                name = (
                    "chicken"
                    if getattr(self.app, "chicken_mode_enabled", None)
                    else build["task"]["fullDisplayName"]
                )

                table.add_row(name, build["why"], timestamp)

            panel_content = table

        else:
            self.log("No queued builds, system is idle.")
            panel_content = Align.center(
                renderable="No builds in the queue.", vertical="middle"
            )

        self.renderable = panel_content

    async def _update(self):
        """Update the current renderable object."""
        await self._get_renderable()
        self.refresh(layout=True)

    async def on_mount(self):
        """Actions that are executed when the widget is mounted."""
        await self._update()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return Panel(renderable=self.renderable, title="queued", expand=True)
