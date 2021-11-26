from __future__ import annotations

from enum import Enum

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from textual.message import Message, MessageTarget
from textual.widget import Widget


class FlashMessageType(Enum):
    """An enum containing valid flash message types."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ShowFlashNotification(Message):
    """A message to signal the flash widget display."""

    def __init__(
        self,
        sender: MessageTarget,
        value: str,
        type: FlashMessageType = FlashMessageType.INFO,
    ) -> None:
        """A message to signal the flash widget display.

        Args:
            sender (MessageTarget): The sender of the message.
            value (str): The value of the message. This will be displayed in the flash widget.
            type (FlashMessageType): The flash message type. Defaults to FlashMessageType.INFO.
        """

        self.value = value
        self.type = type
        super().__init__(sender)


class FlashWidget(Widget):
    """A widget for showing temporary status updates"""

    def __init__(self, timeout: int = 10) -> None:
        """A widget for showing temporary status updates

        Args:
            timeout (int): Time until the flash message disappears in seconds. Defaults to 5.
        """

        name = self.__class__.__name__
        super().__init__(name=name)
        self.timeout = timeout
        self.visible = False
        self.layout_size = 1
        self.style: Style | str = ""
        self.message_type = {
            "success": {
                "emoji": "✅",
                "style": Style(bgcolor="green", color="white", bold=True),
            },
            "error": {
                "emoji": "🔥",
                "style": Style(bgcolor="red3", color="white", bold=True),
            },
            "warning": {
                "emoji": "⚠️",
                "style": Style(bgcolor="dark_orange", color="white", bold=True),
            },
            "info": {
                "emoji": "ℹ️",
                "style": Style(bgcolor="blue", color="white", bold=True),
            },
        }

    async def update_flash_message(self, type: FlashMessageType, value: str) -> None:
        """Update the flash message.

        Args:
            type (FlashMessageType): The flash message type.
            value (str): A value to display.
        """

        self.log("Handling ShowFlashNotification message")

        message_type = self.message_type[type.value]

        self.value = f"{message_type['emoji']} {value}"

        style = message_type["style"]
        assert isinstance(style, Style)
        self.style = style

        self.visible = True

        async def hide():
            self.visible = False

        self.set_timer(self.timeout, hide)
        self.refresh()

    def render(self) -> RenderableType:
        """Render the widget.

        Returns:
            RenderableType: Object to be rendered
        """

        return Text(self.value, justify="center", style=self.style)
