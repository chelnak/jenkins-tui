from __future__ import annotations

from rich.console import RenderableType

from typing import Any, Optional
from textual_inputs import TextInput
from rich.text import Text


class TextInputFieldWidget(TextInput):
    """A custom text input field."""

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: str = "",
        placeholder: Text = Text(""),
        title: Text = Text(""),
        choices: list[str] = [],
        required: bool = False,
        width=100,
        border_style="grey82",
    ) -> None:
        """A custom text input field.

        Args:
            choices (list[str], optional): A list of choices for validation. Defaults to [].
            required (bool, optional): Sets the field as mandatory. Defaults to False.
            width (int, optional): A fixed width for the field. Defaults to 100.
            border_style (str, optional): The style of the border. Defaults to "grey82".
        """
        super().__init__(
            name=name,
            value=str(value),  # because bools make len(self.value) fail
            placeholder=placeholder,
            title=title,
            width=width,
            border_style=border_style,
        )
        self.title = title
        self.choices = choices
        self.required = required
        self.original_title = title
        self.original_border_style = self.border_style
        self.layout_size = 3

    async def validate(self) -> bool:
        """Validates the field input against configured criteria."""
        error_border_style = "red"
        if self.choices and self.value not in self.choices:
            self.border_style = error_border_style
            self.title = Text.from_markup(f"{self.title} - [red]Invalid choice![/]")
            return False

        if self.required and (self.value == "" or self.value is None):
            self.border_style = error_border_style
            self.title = Text.from_markup(f"{self.title} - [red]Required field![/]")
            return False

        self.border_style = self.original_border_style
        self.title = self.original_title
        return True
