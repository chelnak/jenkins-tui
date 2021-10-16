import rich.repr
from textual.message import Message
from textual._types import MessageTarget


@rich.repr.auto
class RootClick(Message):
    def __init__(self, sender: MessageTarget) -> None:
        """Represents the message that is sent when a the root node is clicked.

        Args:
            sender (MessageTarget): The class that sent the message.
        """
        super().__init__(sender)
