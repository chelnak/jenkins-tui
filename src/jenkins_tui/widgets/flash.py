from __future__ import annotations

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from textual.widget import Widget
from textual.reactive import Reactive
from textual.message import Message, MessageTarget


class ShowFlashNotification(Message):
    """A message type to signal the flash widget display."""

    def __init__(self, sender: MessageTarget, value: str) -> None:
        self.value = value
        super().__init__(sender)


class FlashWidget(Widget):
    """A widget for showing temporary status updates"""

    style: Reactive[Style] = Style(bgcolor="green", color="white")
    value: Reactive[str] = Reactive("")
    layout_size: Reactive[int] = 1

    def __init__(self, timeout: int = 5) -> None:
        """A widget for showing temporary status updates

        Args:
            timeout (int, optional): Time until the flash message disappears in seconds. Defaults to 5.
        """
        name = self.__class__.__name__
        super().__init__(name=name)
        self.timeout = timeout
        self.visible = False

    async def update_flash_message(self, value: str, style: Style = None) -> None:
        """Update the flash message.

        Args:
            value (str): A value to display
            style (Style, optional): An optional style object. Defaults to None.
        """
        self.log("Handling ShowFlashNotification message")

        if style:
            self.style = style

        self.value = value
        self.visible = True

        async def hide():
            self.visible = False

        self.set_timer(self.timeout, hide)
        self.refresh()

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Text to be rendered
        """
        return Text(self.value, justify="center", style=self.style)
