from __future__ import annotations

from rich.style import Style
from textual.widgets import ScrollView

from ..tree import Tree
from ..widgets import FigletTextWidget, ScrollBarWidget
from .base import BaseView


class SideBarView(BaseView):
    """A view that contains widgets that make up the sidebar."""

    async def set_tree_focus(self) -> None:
        """Set the focus to the tree."""
        await self.app.set_focus(self.tree)

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
        self.tree = Tree()
        self.scroll_view = ScrollView(
            contents=self.tree,
            name="DirectoryScrollView",
        )
        self.scroll_view.vscroll = ScrollBarWidget()

        self.layout.place(
            head=FigletTextWidget(
                text=self.app.title, name="header", style=Style(color="green")
            )
        )
        self.layout.place(tree=self.scroll_view)

        await self.set_tree_focus()
