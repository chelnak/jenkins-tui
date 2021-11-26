from __future__ import annotations

from rich.style import Style
from rich.text import Text
from textual_inputs import TextInput

from .. import styles


class TextInputFieldWidget(TextInput):
    """A custom text input field."""

    def __init__(
        self,
        *,
        name: str | None = None,
        value: str = "",
        default_value: str = "",
        placeholder: Text = Text(""),
        title: Text = Text(""),
        choices: list[str] = [],
        required: bool = False,
        width: int = 100,
        border_style: str | Style = styles.GREY,
    ) -> None:
        """A custom text input field.

        Args:
            name (str | None): The name of the field.
            value (str): The value of the field.
            default_value (str): The default value of the field.
            placeholder (Text): The placeholder text of the field.
            title (Text): The title of the field.
            choices (list[str]): A list of choices for validation. Defaults to [].
            required (bool): Sets the field as mandatory. Defaults to False.
            width (int): A fixed width for the field. Defaults to 100.
            border_style (str, Style): The style of the border. Defaults to "styles.GREY".
        """

        super().__init__(
            name=name,
            value=str(default_value)
            if default_value != ""
            else str(value),  # because bools make len(self.value) fail
            placeholder=placeholder,
            title=title,
        )

        self.title: str | Text = f"[{styles.GREY}]{title}[/]"
        self.choices = choices
        self.required = required
        self.original_title = self.title
        self.border_style = border_style
        self.original_border_style = self.border_style
        self.layout_size = 3
        self.default_value = str(default_value)
        self.width = width

    async def toggle_field_status(self, valid=True) -> None:
        """Toggles field status.

        Args:
            valid (bool): Whether the field is valid or not.
        """

        if not valid:
            self.border_style = styles.RED
        else:
            self.border_style = self.original_border_style

    async def validate(self) -> bool:
        """Validates the field input against configured criteria.

        Returns:
            bool: Whether the value is valid or not.
        """

        error_border_style = styles.RED
        if self.choices and self.value not in self.choices:
            self.border_style = error_border_style
            self.title = Text.from_markup(
                f"{self.title} - [{styles.RED}]Invalid choice![/]"
            )
            return False

        if self.required and (self.value == "" or self.value is None):
            self.border_style = error_border_style
            self.title = Text.from_markup(
                f"{self.title} - [{styles.RED}]Required field![/]"
            )
            return False

        self.border_style = self.original_border_style
        self.title = self.original_title
        return True
