from typing import Optional

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
        name: Optional[str] = None,
        style: Optional[Style] = None,
        layout_size: int = 8,
    ) -> None:
        """A widget that will generate and display figlet text.

        Args:
            text (str, optional): The text that will be rendered in the widget.
            name (str, optional): The name of the widget. Defaults to the name of the class.
            style (Style, optional): The style of the widget.
            layout_size (int, optional): The size of the widget. Defaults to 10.
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

        return Align.left(
            renderable=FigletTextRenderable(text=self.text),
            vertical="middle",
            style=self.style or "",
            pad=False,
        )
