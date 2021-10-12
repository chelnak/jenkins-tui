from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box
from textual.widget import Widget
from textual.events import Mount

from ..client import Jenkins

from datetime import datetime


class ExecutorStatus(Widget):
    """An executor status widget. Used to display running builds on the server."""

    def __init__(self, client: Jenkins) -> None:
        """An executor status widget.

        Args:
            client (ExtendedJenkinsClient): An instance of ExtendedJenkinsClient
        """
        self.client = client
        name = self.__class__.__name__
        super().__init__(name=name)

        self.renderable: RenderableType = ""

    async def _get_renderable(self):
        """Builds a renderable object."""

        running_builds = await self.client.get_running_builds()

        panel_content: RenderableType
        if len(running_builds) > 0:
            self.log("System has running builds, building table.")
            table = Table(expand=True, box=box.SIMPLE)
            table.add_column(header="name", justify="left", no_wrap=True)
            table.add_column(header="node", justify="left", no_wrap=True)
            table.add_column(header="progress", justify="left", no_wrap=True)
            table.add_column(header="timestamp", justify="left", no_wrap=True)

            for build in running_builds:

                timestamp = datetime.utcfromtimestamp(
                    int(build["timestamp"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")

                name = (
                    "chicken"
                    if getattr(self.app, "chicken_mode_enabled", None)
                    else build["name"]
                )

                table.add_row(
                    name,
                    build["node"],
                    f"{build['progress']}%",
                    timestamp,
                )

            panel_content = table

        else:
            self.log("No running builds, system is idle.")
            panel_content = Align.center(renderable="Idle", vertical="middle")

        self.renderable = panel_content

    async def _update(self):
        """Update the current renderable object."""
        await self._get_renderable()
        self.refresh(layout=True)

    async def on_mount(self, event: Mount):
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """
        await self._update()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return Panel(
            renderable=self.renderable, title="build executor status", expand=True
        )
