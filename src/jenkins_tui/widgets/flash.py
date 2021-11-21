from __future__ import annotations

from enum import Enum, EnumMeta

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from textual.message import Message, MessageTarget
from textual.reactive import Reactive
from textual.widget import Widget


class FlashMessageType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ShowFlashNotification(Message):
    """A message type to signal the flash widget display."""

    def __init__(
        self,
        sender: MessageTarget,
        value: str,
        type: FlashMessageType = FlashMessageType.INFO,
    ) -> None:
        self.value = value
        self.type = type
        super().__init__(sender)


class FlashWidget(Widget):
    """A widget for showing temporary status updates"""

    def __init__(self, timeout: int = 10) -> None:
        """A widget for showing temporary status updates

        Args:
            timeout (int, optional): Time until the flash message disappears in seconds. Defaults to 5.
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
            value (str): A value to display
            style (Style, optional): An optional style object. Defaults to None.
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
            RenderableType: Text to be rendered
        """
        return Text(self.value, justify="center", style=self.style)
