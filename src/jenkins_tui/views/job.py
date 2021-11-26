from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from dependency_injector.wiring import Container, Provide, inject
from rich.text import Text
from textual import events
from textual.binding import NoBinding

from ..containers import Container
from ..jenkins import Jenkins
from ..widgets import (
    ButtonWidget,
    FlashMessageType,
    JobDetailsWidget,
    ShowFlashNotification,
    TextWidget,
)
from .base import BaseView
from .build_with_parameters import BuildWithParametersView


class JobView(BaseView):
    """A view that contains widgets that display job information."""

    details: JobDetailsWidget | None = None

    @inject
    def __init__(self, url: str, client: Jenkins = Provide[Container.client]) -> None:
        """A view that contains widgets that display job information.

        Args:
            url (str): The url of the current job.

        # noqa: DAR101 client
        """
        super().__init__()
        self.url = url
        self.path = urlparse(url).path
        self.client = client
        self.buttons: dict[str, ButtonWidget] = {}
        self.job: dict[str, Any] = {}
        self.job_has_parameters: bool = False

        self.bindings.bind("h", "history", show=False)
        self.bindings.bind("b", "build", show=False)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        await self.app.set_focus(self)

        self.log("Updating job")
        await self.update()
        self.log("Finished updating job")
        self.set_interval(20, self.update)

        name = self.job.get("displayName")
        description = self.job.get("description")
        health_report = self.job.get("healthReport")

        self.app.nav.title = name
        description_renderable = Text("")

        if description:
            description_renderable.append(f"{description}\n\n")

        if health_report:
            description_renderable.append(health_report[0]["description"])

        if description_renderable.plain == "":
            self.layout.show_row("text", False)

        self.layout.add_column("col")
        self.layout.add_row("text", size=5)
        self.layout.add_row("body", min_size=20)

        self.layout.add_areas(
            text="col,text",
            body="col,body",
        )

        self.details = JobDetailsWidget(job=self.job)
        self.layout.place(text=TextWidget(text=description_renderable))
        self.layout.place(body=self.details)

        if self.job_has_parameters:
            self.build_with_params = BuildWithParametersView(job=self.job)
            self.build_with_params.visible = False

            self.layout.place(body=self.build_with_params)

    async def update(self) -> None:
        """Updates the current job"""

        self.job = await self.client.get_job(path=self.path)
        if len(self.job["property"]) > 0 and self.job["property"][0].get(
            "parameterDefinitions"
        ):
            self.job_has_parameters = True

        # Update the job details widget if it has been intialized
        if self.details:
            await self.details.update(job=self.job)

        self.refresh(layout=True)

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
        """Handle a key press.

        Args:
            event (events.Key): A key event
        """

        await self.press(event.key)

    async def action_history(self) -> None:
        """Actions that are executed when the history button is pressed."""

        assert isinstance(self.details, JobDetailsWidget)

        self.details.visible = True
        self.build_with_params.visible = False

        await self.app.set_focus(self.details)
        self.layout.require_update()

    async def action_build(self) -> None:
        """Actions that are executed when the build button is pressed."""

        assert isinstance(self.details, JobDetailsWidget)

        if self.job_has_parameters:
            self.details.visible = False
            self.build_with_params.visible = True
            await self.app.set_focus(self.build_with_params)
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

        self.layout.require_update()
