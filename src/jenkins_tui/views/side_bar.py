from __future__ import annotations
from rich.style import Style
from textual.widgets import ScrollView

from .base import BaseView
from ..tree import Tree
from ..widgets import FigletTextWidget, ScrollBarWidget


class SideBarView(BaseView):
    """A view that contains widgets that make up the sidebar."""

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.layout.add_column("col", min_size=25)
        self.layout.add_row("head", size=8)
        self.layout.add_row("tree", min_size=25)
        self.layout.set_align("left", "left")
        self.layout.set_gutter(0, 0)
        self.layout.set_gap(0, 0)

        self.layout.add_areas(
            head="col,head",
            tree="col,tree",
        )

        tree = ScrollView(
            contents=Tree(),
            name="DirectoryScrollView",
        )
        tree.vscroll = ScrollBarWidget()

        self.layout.place(
            head=FigletTextWidget(
                text=self.app.title, name="header", style=Style(color="green")
            )
        )
        self.layout.place(tree=tree)
