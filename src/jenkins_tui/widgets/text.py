from __future__ import annotations

from rich.console import RenderableType
from rich.text import Text
from textual.widget import Widget

from ..renderables import TextRenderable


class TextWidget(Widget):
    """A generic text widget."""

    def __init__(
        self,
        text: str | Text | None = None,
    ) -> None:
        """A generic text widget.

        Args:
            text (str | Text | None): Text to be displayed.
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
