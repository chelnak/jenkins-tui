from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel

from textual.widget import Widget
from textual.reactive import Reactive


class JobInfo(Widget):
    """A job info widget. This displays information about the current job."""

    style: Reactive = Reactive("")

    def __init__(self, title: str = None, text: str = None) -> None:
        """A job info widget. This displays information about the current job.

        Args:
            title (str, optional): The title of the info widget. Defaults to None.
            text (str, optional): The text that will be rendered in the info widget. Defaults to None.
        """
        self.title = title
        self.text = text

        self.defaults = {
            "title": "Welcome!",
            "text": "Welcome to Jenkins TUI! 🚀\n\n👀 Use the navigation fly-out on the left!",
        }

        name = self.__class__.__name__
        super().__init__(name=name)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        _text = self.defaults["text"] if not self.text else self.text
        panel_content = Padding(
            renderable=_text,
            pad=(1, 0, 0, 1),
            style=self.style,
        )

        _title = self.defaults["title"] if not self.title else self.title
        return Panel(renderable=panel_content, title=_title, expand=True)
