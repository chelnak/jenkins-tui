from rich.console import RenderableType
from rich.padding import Padding

from textual.widget import Widget
from textual.reactive import Reactive, watch


class JobInfo(Widget):
    """A job info widget. This displays information about the current job."""

    style: Reactive[str] = Reactive("")
    info_text: Reactive[str] = Reactive("")

    async def on_mount(self, Mount) -> None:
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """

        async def set_text(text: RenderableType) -> None:
            self.info_text = text

        watch(self.app, "info_text", set_text)

    def render(self) -> RenderableType:
        """Overrides render from textual.widget.Widget"""

        default = (
            "Welcome to Jenkins TUI! 🚀\n\n👀 Use the navigation fly-out on the left!"
        )

        return Padding(
            renderable=default if not self.info_text else self.info_text,
            pad=(1, 0, 0, 1),
            style=self.style,
        )
