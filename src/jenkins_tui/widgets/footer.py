from .. import config
from rich.text import Text
from textual.widgets import Footer as TextualFooter
from textual.reactive import Reactive
from rich.style import StyleType


class Footer(TextualFooter):
    """A custom footer widget."""

    style: Reactive[StyleType] = Reactive("")

    def make_key_text(self) -> Text:
        """Create text containing all the keys.

        Returns:
            Text: [description]
        """

        _styles = config.style_map[config.style]

        text = Text(
            style=_styles["footer_style"],
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper()
                if binding.key_display is None
                else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (
                    f" {key_display} ",
                    "reverse" if hovered else _styles["footer_style"],
                ),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text
