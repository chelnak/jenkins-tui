from __future__ import annotations

from textual.layouts.grid import GridLayout
from textual.reactive import Reactive
from textual.view import View
from textual.widgets import ScrollView


class CustomScrollView(ScrollView):
    """A subclass of textual.widgets.ScrollView"""

    origin_view: Reactive[View]

    def __init__(
        self,
        intial_view: View = None,
        name: str | None = None,
    ) -> None:
        """Initialises a new custom ScrollView instance

        Args:
            intial_view (View): The view that will be assigned to the content area.
            name (str | None): The name of the view.
        """
        _name = self.__class__.__name__ if name is None else name
        super().__init__(name=_name)

        self.window = intial_view
        self.origin_view = self.window

    async def update(self, view: View) -> None:
        """Update the content area of the grid view that backs ScrollView.

        Args:
            view (View): The view that will replace the current one assigned to the content area.
        """
        assert isinstance(self.layout, GridLayout)
        widgets = self.layout.widgets

        del widgets[self.window]
        self.window = view
        self.layout.place(content=view)

        await self.refresh_layout()
