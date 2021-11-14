from __future__ import annotations

from typing import Optional

from rich.console import RenderableType
from textual.widget import Widget

from rich.text import Text
from rich.padding import Padding

from ..renderables import InfoRenderable


class InfoWidget(Widget):
    """A generic info widget. This displays information with a ruled title and some text"""

    def __init__(
        self,
        title: str | Text,
        renderable: str | Text | RenderableType,
    ) -> None:
        """A generic info widget. This displays information with a ruled title and some text.

        Args:
            title (str, Text): The title of the info widget.
            renderable (str, Text): The text that will be rendered in the info widget.
        """
        self.title = title
        self.renderable = renderable

        name = self.__class__.__name__
        super().__init__(name=name)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return InfoRenderable(
            title=self.title,
            renderable=self.renderable,
        )
