from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlparse
from dependency_injector.wiring import Provide, inject

from rich.console import Group, RenderableType
from rich.style import Style
from rich.table import Table
from rich.align import Align
from rich import box
from rich.text import Text
from textual.widget import Widget

from ..client import Jenkins
from ..containers import Container


class JenkinsBuildChangesTable(Widget):
    """ """

    @inject
    def __init__(self, url: str, client: Jenkins = Provide[Container.client]) -> None:
        """

        Args:
            client (ExtendedJenkinsClient): An instance of ExtendedJenkinsClient.
            url (str): The url of the current build.
        """
        self.client: Jenkins = client
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

        panel_content: RenderableType = ""
        if current_job_builds and len(current_job_builds) > 0:
            self.log("Job has changesets, building table.")

            for build in current_job_builds:

                if len(build["changeSets"]) > 0:

                    timestamp = datetime.fromtimestamp(
                        int(build["timestamp"]) / 1000
                    ).strftime("%Y-%m-%d %H:%M:%S")

                    panel_content += f"[bold]#{build['number']} {timestamp}[/]\n"
                    for x, y in enumerate(build["changeSets"][0]["items"]):
                        panel_content += f"""{x+1}. {y["comment"]}\r"""

                    panel_content += "\n\n"

        else:
            self.log("No changesets for current job.")
            panel_content = Align.center(
                renderable="There are currently no changesets for this job.",
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
