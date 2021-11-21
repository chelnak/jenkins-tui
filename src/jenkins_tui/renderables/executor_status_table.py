from __future__ import annotations

from typing import Any

from rich.console import Group
from rich.padding import Padding
from rich.progress import BarColumn, Progress
from rich.rule import Rule
from rich.table import Table

from .. import styles
from .paginated_table import PaginatedTableRenderable


class ExecutorStatusTableRenderable(PaginatedTableRenderable):
    """A renderable that displays execution status."""

    def __init__(
        self,
        builds: list[dict[str, Any]],
        page_size: int = -1,
        page: int = 1,
        row: int = 0,
    ) -> None:
        """A renderable that displays execution status.

        Args:
            builds (list[dict[str, Any]]): A list of builds to display.
            page_size (int, optional): The size of the page before pagination happens. Defaults to -1.
            page (int, optional): The starting page. Defaults to 1.
            row (int, optional): The starting row. Defaults to 0.
        """
        self.builds = builds
        super().__init__(
            len(builds), page_size=page_size, page=page, row=row, row_size=3
        )

    def renderables(self, start_index: int, end_index: int) -> list[dict[str, Any]]:
        return self.builds[start_index:end_index]

    def render_rows(self, table: Table, renderables: list[dict[str, Any]]) -> None:
        for build in renderables:
            name = build["name"]

            progress = Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
            )

            completed = 0 if build["progress"] == -1 else build["progress"]
            progress.add_task(
                "[green]➜ [/]",
                completed=completed,
            )
            render_group = Group(
                *[
                    f"[{styles.GREY}][bold]{name}[/][/]",
                    progress.get_renderable(),
                    Rule(style=styles.GREY),
                ]
            )
            table.add_row(Padding(render_group, pad=(0, 1)))

    def render_columns(self, table: Table) -> None:
        table.show_header = False
        table.add_column(no_wrap=True)
