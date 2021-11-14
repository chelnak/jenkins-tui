from __future__ import annotations

from datetime import datetime
from typing import Any
from rich.table import Table

from rich.table import Table

from .paginated_table import PaginatedTableRenderable


class BuildChangesTableRenderable(PaginatedTableRenderable):
    """A renderable that displays build changes."""

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
            title (str): The title of the table.
            page_size (int, optional): The size of the page before pagination happens. Defaults to -1.
            page (int, optional): The starting page. Defaults to 1.
            row (int, optional): The starting row. Defaults to 0.
        """
        super().__init__(len(builds), page_size=page_size, page=page, row=row)
        self.builds = builds
        self.title = title

    def build_table(self) -> Table:
        return Table(title_style="", expand=True, box=None, show_edge=True)

    def renderables(self, start_index: int, end_index: int) -> list[dict[str, Any]]:
        return self.builds[start_index:end_index]

    def render_rows(self, table: Table, renderables: list[dict[str, Any]]) -> None:

        for build in renderables:

            if len(build.get("changeSets", [])) > 0:

                timestamp = datetime.fromtimestamp(
                    int(build["timestamp"]) / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")

                panel_content = ""
                for x, y in enumerate(build["changeSets"][0]["items"]):
                    panel_content += f"""{x+1}. {y["comment"]}\r"""

                table.add_row(
                    f"[bold]#{build['number']} ({timestamp})[/]\n\n{panel_content}"
                )

    def render_columns(self, table: Table) -> None:
        # table.add_column("", header_style="grey82 bold", ratio=20, no_wrap=True)
        table.add_column("", header_style="grey82 bold", no_wrap=True)
        # table.add_column("timestamp", header_style="grey82 bold", no_wrap=True)
