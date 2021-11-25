from __future__ import annotations

from typing import Optional

from rich.console import RenderableType
from rich.text import Text
from textual.widget import Widget

from ..renderables import TextRenderable


class TextWidget(Widget):
    """A generic text widget."""

    def __init__(
        self,
        text: Optional[str | Text] = None,
    ) -> None:
        """A generic text widget.

        Args:
            text (Optional[str | Text]): Text to be displayed
        """

        self.text = text or ""
        name = self.__class__.__name__
        super().__init__(name=name)

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        return TextRenderable(
            text=self.text,
        )
