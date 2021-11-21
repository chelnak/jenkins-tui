from __future__ import annotations

from urllib.parse import urlparse

from dependency_injector.wiring import Container, Provide, inject
from rich.text import Text
from textual import events
from textual.binding import NoBinding

from ..client import Jenkins
from ..containers import Container
from ..widgets import (
    ButtonWidget,
    FlashMessageType,
    JobDetailsWidget,
    NavWidget,
    ShowFlashNotification,
    TextWidget,
)
from .base import BaseView
from .build_with_parameters import BuildWithParametersView


class JobView(BaseView):
    """A view that contains widgets that display job information."""

    current_button: ButtonWidget | None = None

    @inject
    def __init__(self, url: str, client: Jenkins = Provide[Container.client]) -> None:
        """A view that contains widgets that display job information.

        Args:
            url (str): The url of the current job.
            client (Jenkins, optional): An injected Jenkins http client instance. Defaults to Provide[Container.client].
        """
        super().__init__()
        self.url = url
        self.path = urlparse(url).path
        self.client = client
        self.buttons: dict[str, ButtonWidget] = {}
        self.job_has_parameters: bool = False

        self.bindings.bind("h", "history", show=False)
        self.bindings.bind("b", "build", show=False)

    async def get_job(self) -> dict:
        """Get job information from the server.

        Returns:
            dict: A dictionary containing job information.
        """
        job = await self.client.get_job(path=self.path)
        if len(job["property"]) > 0 and job["property"][0].get("parameterDefinitions"):
            self.job_has_parameters = True

        return job

    async def press(self, key: str) -> bool:
        """Handle a key press.

        Args:
            key (str): A key

        Returns:
            bool: True if the key was handled by a binding, otherwise False
        """
        try:
            binding = self.bindings.get_key(key)
        except NoBinding:
            return False
        else:
            await self.action(binding.action)
        return True

    async def on_key(self, event: events.Key) -> None:
        await self.press(event.key)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        await self.app.set_focus(self)

        job = await self.get_job()
        name = job["displayName"]

        self.layout.add_column("col")
        self.layout.add_row("nav", size=8)
        self.layout.add_row("text", size=5)
        self.layout.add_row("details", min_size=20)
        self.layout.add_row("build_view", min_size=20)
        self.layout.show_row("build_view", False)

        self.layout.add_areas(
            nav="col,nav",
            text="col,text",
            details="col,details",
            build_view="col,build_view",
        )

        description = Text("")

        if job["description"] != "":
            description.append(f"{job['description']}\n\n")

        if job["healthReport"]:
            description.append(job["healthReport"][0]["description"])

        self.details = JobDetailsWidget(path=self.path)

        if description.plain == "":
            self.layout.show_row("text", False)

        self.layout.place(nav=NavWidget(title=name))
        self.layout.place(text=TextWidget(text=description))
        self.layout.place(details=self.details)

        if self.job_has_parameters:
            self.build_with_params = BuildWithParametersView(job=job)
            self.layout.place(build_view=self.build_with_params)

    async def action_history(self) -> None:
        """Actions that are executed when the history button is pressed."""
        self.layout.show_row("build_view", False)
        self.layout.show_row("details", True)

        self.details.render_history_table()
        self.details.refresh()

        await self.app.set_focus(self.details)
        self.refresh(layout=True)

    async def action_build(self) -> None:
        """Actions that are executed when the build button is pressed."""

        if self.job_has_parameters:
            self.layout.show_row("build_view", True)
            self.layout.show_row("details", False)
            self.build_with_params.visible = True
            await self.app.set_focus(self.build_with_params)
            self.build_with_params.refresh()
        else:

            try:
                await self.client.build(path=self.path)
                await self.post_message_from_child(
                    ShowFlashNotification(
                        self, type=FlashMessageType.SUCCESS, value="Build scheduled"
                    )
                )
            except Exception as e:
                await self.post_message_from_child(
                    ShowFlashNotification(
                        self, type=FlashMessageType.ERROR, value=str(e)
                    )
                )

        self.details.refresh()
        self.refresh(layout=True)
