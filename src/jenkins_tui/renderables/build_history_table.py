from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.style import Style
from rich.table import Table
from rich.text import Text

from .. import styles
from .paginated_table import PaginatedTableRenderable


class BuildHistoryTableRenderable(PaginatedTableRenderable):
    """A renderable that displays build history."""

    def __init__(
        self,
        builds: list[dict[str, Any]],
        title: str,
        page_size: int = -1,
        page: int = 1,
        row: int = 0,
    ) -> None:
        """A renderable that displays build history.

        Args:
            builds (list[dict[str, Any]]): A list of builds to display.
            title (str): Title of the table.
            page_size (int): The size of the page before pagination happens. Defaults to -1.
            page (int): The starting page. Defaults to 1.
            row (int): The starting row. Defaults to 0.
        """

        self.builds = builds
        self.title = title

        super().__init__(
            len(builds), page_size=page_size, page=page, row=row, row_size=1
        )

    def _get_style_from_result(self, result: str) -> str | Style:
        """Returns a style for a given result.

        Args:
            result (str): Result of the current build. It can be one of [SUCCESS, FAILURE, ABORTED, IN PROGRESS, NOT BUILT]

        Returns:
            str | Style: A Rich Style object or a string repesenting a color
        """

        result_style_map: dict[str, str | Style]
        result_style_map = {
            "SUCCESS": styles.GREEN,
            "FAILURE": styles.RED,
            "ABORTED": styles.ORANGE,
            "IN PROGRESS": styles.ORANGE,
            "NOT BUILT": "",
        }

        return result_style_map[result]

    def renderables(self, start_index: int, end_index: int) -> list[dict[str, Any]]:
        """Generate a list of renderables.

        Args:
            start_index (int): The starting index.
            end_index (int): The ending index.

        Returns:
            list[dict[str, Any]]: A list of renderables.
        """

        return self.builds[start_index:end_index]

    def render_rows(self, table: Table, renderables: list[dict[str, Any]]) -> None:
        """Renders rows for the table.

        Args:
            table (Table): The table to render rows for.
            renderables (list[dict[str, Any]]): The renderables to render.
        """

        for build in renderables:

            timestamp = datetime.fromtimestamp(int(build["timestamp"]) / 1000).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            result_text = build["result"] if build["result"] else "IN PROGRESS"

            result = Text(
                text=result_text,
                style=self._get_style_from_result(result_text),
            )

            table.add_row(f"{build['number']}", build["description"], result, timestamp)

    def render_columns(self, table: Table) -> None:
        """Renders columns for the table.

        Args:
            table (Table): The table to render columns for.
        """

        table.add_column("#", header_style=f"{styles.GREY} bold")
        table.add_column(
            "description", header_style=f"{styles.GREY} bold", no_wrap=True, ratio=40
        )
        table.add_column("result", header_style=f"{styles.GREY} bold")
        table.add_column("timestamp", header_style=f"{styles.GREY} bold", no_wrap=True)
