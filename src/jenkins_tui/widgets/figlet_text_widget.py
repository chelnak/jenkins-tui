from __future__ import annotations

from rich.align import Align
from rich.console import RenderableType
from rich.style import Style
from textual.reactive import Reactive
from textual.widget import Widget

from ..renderables import FigletTextRenderable


class FigletTextWidget(Widget):
    """A widget that will generate and display figlet text."""

    has_focus = Reactive(False)
    mouse_over: bool = Reactive(False)

    def __init__(
        self,
        text: str,
        name: str | None = None,
        style: Style | None = None,
        layout_size: int = 8,
    ) -> None:
        """A widget that will generate and display figlet text.

        Args:
            text (str): The text that will be rendered in the widget.
            name (str | None): The name of the widget. Defaults to the name of the class.
            style (Style | None): The style of the widget.
            layout_size (int): The size of the widget. Defaults to 10.
        """

        super().__init__(name=name or self.__class__.__name__)
        self.text = text
        self.layout_size = layout_size
        self.style = style

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def on_focus(self) -> None:
        self.has_focus = True

    def on_blur(self) -> None:
        self.has_focus = False

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        return Align.left(
            renderable=FigletTextRenderable(text=self.text),
            vertical="middle",
            style=self.style or "",
            pad=False,
        )
