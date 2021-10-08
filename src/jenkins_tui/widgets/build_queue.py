from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box
from textual.widget import Widget
from textual.events import Mount

from datetime import datetime

from ..jenkins_http import ExtendedJenkinsClient


class BuildQueue(Widget):
    """An build queue widget. Used to display queued builds on the server."""

    def __init__(self, client: ExtendedJenkinsClient) -> None:
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

        queue_url = (
            f"{self.client.server}/queue/api/json?tree=items[id,inQueueSince,why]"
        )
        r = await self.client.custom_async_http_requst(sender=self, url=queue_url)
        response = r.json()
        queue = response["items"]

        panel_content: RenderableType
        if len(queue) > 0:
            self.log("System has queued buids, building table.")
            table = Table(expand=True, box=box.SIMPLE)
            table.add_column(header="id", justify="right", no_wrap=True)
            table.add_column(header="reason", justify="left", no_wrap=True)
            table.add_column(header="queued since", justify="left", no_wrap=True)

            for build in queue:

                timestamp = datetime.utcfromtimestamp(
                    int(build["inQueueSince"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")

                table.add_row(str(build["id"]), build["why"], timestamp)

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
        self.refresh()

    async def on_mount(self, event: Mount):
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """
        await self._get_renderable()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return Panel(renderable=self.renderable, title="build queue", expand=True)
