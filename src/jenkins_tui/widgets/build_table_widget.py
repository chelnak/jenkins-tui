from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlparse
from dependency_injector.wiring import Provide, inject

from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.align import Align
from rich import box
from rich.text import Text
from textual.widget import Widget

from ..client import Jenkins
from ..containers import Container


class JenkinsBuildTable(Widget):
    """A build table widget. Used to display builds within a job."""

    @inject
    def __init__(self, url: str, client: Jenkins = Provide[Container.client]) -> None:
        """A build table widget.

        Args:
            client (ExtendedJenkinsClient): An instance of ExtendedJenkinsClient.
            url (str): The url of the current build.
        """
        self.client = client
        self.current_job_url = url
        name = self.__class__.__name__
        super().__init__(name=name)
        self.renderable: RenderableType = ""

    def _get_style_from_result(self, result: str) -> str | Style:
        """Returns a style for a given result.

        Args:
            result (str): Result of the current build. It can be one of [SUCCESS, FAILURE, ABORTED, IN PROGRESS, NOT BUILT]

        Returns:
            str | Style: A Rich Style object or a string repesenting a color
        """

        result_style_map: dict[str, str | Style]
        result_style_map = {
            "SUCCESS": "green",
            "FAILURE": "red",
            "ABORTED": "#d45b0b",
            "IN PROGRESS": Style(color="yellow"),
            "NOT BUILT": "",
        }

        return result_style_map[result]

    async def _get_renderable(self):
        """Builds a renderable object."""

        url = urlparse(self.current_job_url)  # assumption
        current_job_builds = await self.client.get_builds_for_job(path=url.path)

        panel_content: RenderableType
        if current_job_builds and len(current_job_builds) > 0:
            self.log("Job has builds, building table.")
            panel_content = Table(expand=True, box=box.SIMPLE)
            panel_content.add_column(header="#", justify="right")
            panel_content.add_column(header="result", justify="left", no_wrap=True)
            panel_content.add_column(header="duration", justify="right", no_wrap=True)
            panel_content.add_column(header="timestamp", justify="right", no_wrap=True)

            for build in current_job_builds:

                timestamp = datetime.fromtimestamp(
                    int(build["timestamp"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")
                duration = str(timedelta(seconds=int(build["duration"]) / 1000)).split(
                    "."
                )[0]

                result_text = build["result"] if build["result"] else "IN PROGRESS"

                result = Text(
                    text=result_text,
                    style=self._get_style_from_result(result_text),
                )

                panel_content.add_row(f"{build['number']}", result, duration, timestamp)
        else:
            self.log("No builds for current job.")
            panel_content = Align.center(
                renderable="There are currently no builds for this job.",
                vertical="middle",
            )

        self.renderable = panel_content

    async def _update(self):
        """Update the current renderable object."""
        await self._get_renderable()
        self.refresh(layout=True)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """
        await self._update()
        self.set_interval(10, self._update)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""
        return self.renderable
