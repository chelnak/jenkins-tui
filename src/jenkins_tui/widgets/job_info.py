from rich.console import RenderableType
from rich.padding import Padding
from rich.panel import Panel

from textual.widget import Widget
from textual.reactive import Reactive, watch


class JobInfo(Widget):
    """A job info widget. This displays information about the current job."""

    style: Reactive[str] = Reactive("")
    title: Reactive[str] = Reactive("")
    message: Reactive[str] = Reactive("")

    async def on_mount(self, Mount) -> None:
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """

        async def set_title(text: RenderableType) -> None:
            self.title = text

        async def set_message(text: RenderableType) -> None:
            self.message = text

        watch(self.app, "info_title", set_title)
        watch(self.app, "info_message", set_message)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        defaults = {
            "title": "Welcome!",
            "message": "Welcome to Jenkins TUI! 🚀\n\n👀 Use the navigation fly-out on the left!",
        }

        message = defaults["message"] if not self.message else self.message
        panel_content = Padding(
            renderable=message,
            pad=(1, 0, 0, 1),
            style=self.style,
        )

        title = defaults["title"] if not self.title else self.title
        return Panel(renderable=panel_content, title=title, expand=True)
