from __future__ import annotations

from .base import BaseView
from ..tree import Tree
from ..widgets import FigletTextWidget


class SideBarView(BaseView):
    """A view that contains widgets that make up the sidebar."""

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.layout.add_column("col", min_size=25)
        self.layout.add_row("head", size=8)
        self.layout.add_row("tree")
        self.layout.set_align("left", "left")
        self.layout.set_gutter(0, 0)
        self.layout.set_gap(0, 0)

        self.layout.add_areas(
            head="col,head",
            tree="col,tree",
        )

        self.layout.place(head=FigletTextWidget(text=self.app.title, name="header"))
        self.layout.place(tree=Tree())
