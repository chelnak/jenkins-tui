from typing import Dict, List, Union
from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich import box
from rich.text import Text
from textual.widget import Widget
from datetime import datetime, timedelta


class BuildTable(Widget):
    def __init__(self, builds: List[Dict[str, str]]):
        """A build table widget. Used to display builds within a job.

        Args:
            builds (List[Dict[str, str]]): A list of jobs.
        """

        self._builds = builds
        super().__init__()

    def _get_style_from_result(self, result: str) -> Union[str, Style]:
        """Returns a style for a given result.

        Args:
            result (str): Result of the current build. It can be one of [SUCCESS, FAILURE, ABORTED, IN PROGRESS, NOT BUILT]

        Returns:
            Union[str, Style]: A Rich Style object or a string repesenting a color
        """

        result_style_map: dict[str, Union[str, Style]]
        result_style_map = {
            "SUCCESS": "green",
            "FAILURE": "red",
            "ABORTED": "#d45b0b",
            "IN PROGRESS": Style(color="yellow"),
            "NOT BUILT": "",
        }

        return result_style_map[result]

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        table = Table(expand=True, box=box.SIMPLE)
        table.add_column(header="#", justify="right")
        table.add_column(header="result", justify="left", no_wrap=True)
        table.add_column(header="duration", justify="right", no_wrap=True)
        table.add_column(header="timestamp", justify="right", no_wrap=True)

        for build in self._builds:

            timestamp = datetime.utcfromtimestamp(
                int(build["timestamp"]) / 1000
            ).strftime("%Y-%m-%d %H:%M:%S")
            duration = str(timedelta(seconds=int(build["duration"]) / 1000)).split(".")[
                0
            ]

            result_text = build["result"] if build["result"] else "IN PROGRESS"

            result = Text(
                text=result_text,
                style=self._get_style_from_result(result_text),
            )

            table.add_row(f"{build['number']}", result, duration, timestamp)

        return Panel(renderable=table, title="builds", expand=True)
