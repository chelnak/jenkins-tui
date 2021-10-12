from __future__ import annotations
from typing import List

from textual.widget import Widget


from rich.console import RenderableType

from textual.widgets import ScrollView


class TestScrollView(ScrollView):
    def __init__(self, contents: List[RenderableType | Widget]) -> None:
        super().__init__()

        from .window_view import WindowView

        self.window = WindowView(contents)

    async def update(self, widgets: List[RenderableType], home: bool = True) -> None:
        if home:
            self.home()
        await self.window.update(widgets=widgets)
