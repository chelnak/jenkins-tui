import rich.repr
from textual.message import Message
from textual._types import MessageTarget


@rich.repr.auto
class JobClick(Message):
    def __init__(self, sender: MessageTarget, name: str, url: str) -> None:
        """Represents the message that is sent when a job node is clicked.

        Args:
            sender (MessageTarget): The class that sent the message.
            name (str): The name of the node.
            url (str): The url used for retrieving more information.
        """

        self.node_name = name
        self.url = url
        super().__init__(sender)
