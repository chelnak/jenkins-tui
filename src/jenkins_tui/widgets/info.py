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
        title: str = None,
        renderable: Optional[str | Text | RenderableType] = None,
    ) -> None:
        """A generic info widget. This displays information with a ruled title and some text.

        Args:
            title (str, optional): The title of the info widget. Defaults to None.
            renderable (str, Text, optional): The text that will be rendered in the info widget. Defaults to None.
        """
        self.title = title
        self.renderable = renderable

        self.defaults = {
            "title": "Welcome!",
            "renderable": "Welcome to Jenkins TUI! 🚀\n\n👀 Use the navigation fly-out on the left!",
        }

        name = self.__class__.__name__
        super().__init__(name=name)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        return Padding(
            InfoRenderable(
                title=self.title or self.defaults["title"],
                renderable=self.renderable or self.defaults["renderable"],
            ),
            pad=(4, 0, 0, 0),
        )
