from __future__ import annotations
from abc import ABC, abstractmethod
from math import ceil
from typing import Any, List, Union

from rich import box
from rich.console import Group
from rich.padding import Padding
from rich.style import Style
from rich.table import Table
from rich.text import Text

from textual.reactive import Reactive


class PaginatedTableRenderable(ABC):
    """This class originates from here: https://github.com/sauljabin/kaskade/blob/main/kaskade/renderables/paginated_table.py"""

    __page: int = 1
    __row: int = 0
    __is_clickable: Reactive[bool] = Reactive(True)

    def __init__(
        self,
        total_items: int,
        page_size: int = -1,
        row_size=1,
        page: int = 1,
        row: int = 0,
    ) -> None:
        self.total_items = total_items
        self.page_size = total_items if page_size < 0 else page_size
        self.row_size = row_size
        if row > 0:
            self.row = row

    def total_pages(self) -> int:
        return 0 if self.page_size <= 0 else ceil(self.total_items / self.page_size)

    @property
    def is_clickable(self) -> bool:
        return self.__is_clickable

    @is_clickable.setter
    def is_clickable(self, value: bool) -> None:
        self.__is_clickable.set(value)

    @property
    def row(self) -> int:
        return self.__row

    @row.setter
    def row(self, row: int) -> None:
        if row <= 0:
            self.__row = self.current_page_size()
        elif row > self.current_page_size():
            self.__row = 1
        else:
            self.__row = row

    def current_page_size(self) -> int:
        renderables = self.renderables(self.start_index(), self.end_index())
        return len(renderables)

    def previous_row(self) -> None:
        self.row -= 1

    def next_row(self) -> None:
        self.row += 1

    @property
    def page(self) -> int:
        return self.__page

    @page.setter
    def page(self, page: int) -> None:
        if page <= 0:
            self.__page = 1
        elif page > self.total_pages():
            self.__page = self.total_pages()
        else:
            self.__page = page

        self.__row = 0

    def first_page(self) -> None:
        self.page = 1

    def last_page(self) -> None:
        self.page = self.total_pages()

    def previous_page(self) -> None:
        self.page -= 1

    def next_page(self) -> None:
        self.page += 1

    @abstractmethod
    def render_columns(self, table: Table) -> None:
        pass

    @abstractmethod
    def render_rows(self, table: Table, renderables: List[Any]) -> None:
        pass

    @abstractmethod
    def renderables(self, start_index: int, end_index: int) -> List[Any]:
        pass

    def build_table(self) -> Table:
        return Table(title_style="", expand=True, box=box.SIMPLE)

    def __rich__(self) -> Union[Group, str]:
        pagination_info = Text(
            justify="right",
        )

        if self.total_pages() > 0:
            pagination_info += Text.from_markup(
                "[gray82]page [bold]{}[/] of [bold]{}[/][/]".format(
                    self.page, self.total_pages()
                ),
            )
        else:
            pagination_info += ""

        table = self.build_table()
        self.render_columns(table)

        renderables = self.renderables(self.start_index(), self.end_index()) or []
        self.render_rows(table, renderables)

        if len(table.rows) > self.page_size:
            return (
                f"Rows {len(table.rows)} greater than [yellow bold]{self.page_size}[/]"
            )

        if 0 < self.row <= len(table.rows):
            table.rows[self.row - 1].style = Style(
                bold=True, dim=False, bgcolor="grey35"
            )

        missing_rows = self.page_size - len(table.rows) * self.row_size
        multip = missing_rows
        padding = Padding(
            Padding(pagination_info, (0, 1, 0, 0)),
            (missing_rows, 0, 0, 0),
        )

        return Group(table, padding)

    def start_index(self) -> int:
        return (self.page - 1) * self.page_size

    def end_index(self) -> int:
        return self.page * self.page_size

    def __str__(self) -> str:
        renderables = self.renderables(self.start_index(), self.end_index()) or []
        return str(renderables)
