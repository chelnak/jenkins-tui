from __future__ import annotations
from typing import Any

from dependency_injector.wiring import Container, Provide, inject

from rich.style import Style
from rich.text import Text

from textual.views import GridView
from textual.layouts.grid import GridLayout
from textual.widget import Widget
from textual.widgets import ButtonPressed

from ..client import Jenkins
from ..widgets import ButtonWidget, TextInputFieldWidget, ShowFlashNotification
from ..containers import Container
from .base import BaseView


class BuildWithParametersView(BaseView):
    """Used to display the build with parameters options."""

    @inject
    def __init__(
        self, job: dict[str, Any], client: Jenkins = Provide[Container.client]
    ) -> None:
        """Used to display the build with parameters options.

        Args:
            job (dict[str, Any]): A job dictionary.
            client (Jenkins, optional): An injected Jenkins http client instance. Defaults to Provide[Container.client].
        """
        super().__init__()

        self.layout = GridLayout()
        self.job = job
        self.client = client
        self.fields: list[Widget] = []
        self.current_button: ButtonWidget | None = None

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.layout.add_column("col1", size=60)
        self.layout.set_align("center")
        self.layout.set_gutter(0, 0)

        # Fields
        for parameter in self.job["property"][0]["parameterDefinitions"]:

            self.log(f"parameter {parameter['name']}")
            name = parameter["name"]
            title = name.lower().replace("_", " ").capitalize()
            placeholder = Text(
                parameter["description"] or "", style=Style(italic=True, dim=True)
            )

            field = TextInputFieldWidget(
                name=name,
                title=title,
                placeholder=placeholder,
                value=parameter["defaultParameterValue"].get("value"),
                choices=parameter.get("choices", []),
                # validation_regex=parameter.get("validationRegex", None),
            )

            self.layout.add_row(f"row_{name}", size=3)
            self.fields.append(field)

        self.layout.place(*self.fields)

        # Buttons
        self.layout.add_row("row_buttons")
        await self.add_button("OK")
        await self.add_button("Cancel")

        buttons_view = GridView()
        buttons_view.grid.add_column("ok", size=15)
        buttons_view.grid.add_column("cancel", size=15)
        buttons_view.grid.add_row("row", size=3)
        buttons_view.grid.set_align("center", "center")
        buttons_view.grid.set_gutter(0, 0)
        buttons_view.grid.place(*list(self.buttons.values()))

        self.layout.place(*[buttons_view])

        await self.refresh_layout()

    async def handle_button_pressed(self, message: ButtonPressed):
        # reset previous current button toggle value
        self.log(f"button pressed {message.name}")
        if self.current_button:
            self.current_button.toggle = False

        # set new current button toggle value
        self.current_button = message.sender
        assert isinstance(self.current_button, ButtonWidget)
        self.current_button.toggle = True

        if message.sender.name == "ok":

            parameters = {}
            validation_failed = False
            for field in self.fields:
                valid = await field.validate()
                parameters[field.name] = field.value
                if not valid:
                    validation_failed = True
                    self.current_button.toggle = False

            message.stop()

            if not validation_failed:
                field.value = ""

                await self.client.build(path=self.parent.path, parameters=parameters)

                self.post_message(
                    ShowFlashNotification(self, value="Build scheduled ✅")
                )

                await self.post_message(ButtonPressed(self.parent.nav.buttons["build"]))

        self.refresh()