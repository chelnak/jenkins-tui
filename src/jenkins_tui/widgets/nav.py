from __future__ import annotations

import rich.repr
from rich import box
from rich.align import Align
from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from textual.widget import Widget

from .. import styles


@rich.repr.auto
class NavWidget(Widget):
    def __init__(self, title: str | Text) -> None:
        self.keys: list[tuple[str, str]] = []
        super().__init__()
        self.layout_size = 1
        self._key_text: Text | None = None
        self.title = title

    def __rich_repr__(self) -> rich.repr.Result:
        yield "keys", self.keys

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style=f"{styles.GREY} dim",
            no_wrap=True,
            overflow="ellipsis",
            justify="right",
            end="",
        )

        bindings = self.app.bindings.shown_keys + self.parent.bindings.shown_keys

        for binding in bindings:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            key_text = Text.assemble(
                f" {binding.description} ",
                (f"[{key_display}]"),
            )
            text.append_text(key_text)

        return text

    def render(self) -> RenderableType:
        if self._key_text is None:
            self._key_text = self.make_key_text()
        title = Align.center(
            renderable=Text(
                self.title,
                style=Style(color=styles.GREY, bold=True),
            )
            if isinstance(self.title, str)
            else self.title,
            vertical="middle",
            pad=False,
            height=4,
        )

        head = Panel(
            Group(title, self._key_text),
            box=styles.BOX,
            height=7,
            border_style=Style(color=styles.PURPLE),
            padding=(0, 0, 0, 0),
        )

        return Padding(head, pad=(1, 0, 0, 0))
