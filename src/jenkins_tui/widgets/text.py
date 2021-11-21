from __future__ import annotations

from typing import Optional

from rich.console import RenderableType
from rich.text import Text
from textual.widget import Widget

from ..renderables import TextRenderable


class TextWidget(Widget):
    """A generic info widget. This displays information with a ruled title and some text"""

    def __init__(
        self,
        text: Optional[str | Text | RenderableType] = None,
    ) -> None:
        """A generic info widget. This displays information with a ruled title and some text.

        Args:
            title (str, Text): The title of the info widget.
            renderable (str, Text): The text that will be rendered in the info widget.
        """
        self.text = text or ""

        name = self.__class__.__name__
        super().__init__(name=name)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return TextRenderable(
            text=self.text,
        )
