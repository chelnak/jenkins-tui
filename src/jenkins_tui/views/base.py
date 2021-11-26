from __future__ import annotations

from rich.text import Text
from textual import events, messages
from textual.binding import Bindings
from textual.geometry import Size, SpacingDimensions
from textual.layouts.grid import GridLayout
from textual.reactive import Reactive
from textual.view import View
from textual.views._window_view import WindowChange

from ..widgets import ButtonWidget


class BaseView(View):
    """A base view containing common properties and methods."""

    visible: Reactive[bool] = Reactive(True)

    def __init__(self) -> None:
        """A base view containing common properties and methods."""

        gutter: SpacingDimensions = (1, 0)
        name = self.__class__.__name__
        layout = GridLayout(gap=(1, 1), gutter=gutter, align=("center", "top"))
        super().__init__(name=name, layout=layout)

        self.layout: GridLayout = layout
        self.buttons: dict[str, ButtonWidget] = {}
        self.bindings = Bindings()

    async def add_button(self, text: str, id: str | None = None) -> None:
        """Add a button to the view.

        Args:
            text (str): This is the text that will be displayed on the button.
            id (str | None): The id of the button. Defaults to None.
        """

        if id is None:
            id = text.lower()

        label = Text(text=text)
        button = ButtonWidget(label=label, name=id)
        self.buttons[id] = button

    async def on_hide(self) -> None:
        self.visible = False

    async def on_show(self) -> None:
        self.visible = True

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""
        pass

    async def handle_layout(self, message: messages.Layout) -> None:
        """Handle a layout message.

        Args:
            message (messages.Layout): The message to handle.
        """

        self.layout.require_update()
        message.stop()
        self.refresh()

    async def handle_update(self, message: messages.Update) -> None:
        """Handle an update message.

        Args:
            message (messages.Update): The message to handle.
        """

        message.prevent_default()
        await self.emit(WindowChange(self))

    async def watch_scroll_x(self, value: int) -> None:
        self.layout.require_update()
        self.refresh()

    async def watch_scroll_y(self, value: int) -> None:
        """Watch the scrol_y attribute.

        Args:
            value (int): The new value of the scroll_y attribute.
        """

        self.layout.require_update()
        self.refresh()

    async def watch_virtual_size(self, size: Size) -> None:
        """Watch the virtual_size attribute.

        Args:
            size (Size): The new value of the virtual_size attribute.
        """

        await self.emit(WindowChange(self))

    async def on_resize(self, event: events.Resize) -> None:
        """Events that are executed when the window is resized.

        Args:
            event (events.Resize): A resize event.
        """

        await self.emit(WindowChange(self))
