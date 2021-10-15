from __future__ import annotations

from textual.layouts.grid import GridLayout
from textual.view import View
from textual.widgets import ScrollView

from .home_view import JenkinsHomeView
from ..widgets import JenkinsScrollBar


class JenkinsScrollView(ScrollView):
    """A subclass of textual.widgets.ScrollView"""

    def __init__(self) -> None:
        """Initialises a new custom ScrollView instance."""
        name = self.__class__.__name__
        super().__init__(name=name)
        self.window = JenkinsHomeView()
        self.vscroll = JenkinsScrollBar()

    async def update(self, view: View) -> None:
        """Update the content area of the grid view that backs ScrollView.

        Args:
            view (View): The view that will replace the current one assigned to the content area.
        """
        assert isinstance(self.layout, GridLayout)
        widgets = self.layout.widgets

        # noice!
        del widgets[self.window]
        self.window = view
        self.layout.place(content=view)

        # horrible
        # for widget, _area in widgets.items():
        #     if _area == area:
        #         del widgets[widget]
        #         widgets[view] = area
        #         break

        await self.refresh_layout()
