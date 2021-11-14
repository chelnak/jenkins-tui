from __future__ import annotations

from urllib.parse import urlparse
from dependency_injector.wiring import Container, Provide, inject

from textual import events
from textual.widgets import ButtonPressed

from ..client import Jenkins
from ..widgets import InfoWidget, JobDetailsWidget, ButtonWidget

from ..containers import Container
from .base import BaseView
from .job_nav import JobNavView
from .build_with_parameters import BuildWithParametersView
from ..widgets import ShowFlashNotification, FlashMessageType


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

    async def get_job(self) -> dict:
        """Get job information from the server.

        Returns:
            dict: A dictionary containing job information.
        """
        job = await self.client.get_job(path=self.path)
        if len(job["property"]) > 0 and job["property"][0].get("parameterDefinitions"):
            self.job_has_parameters = True

        return job

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        job = await self.get_job()
        name = job["displayName"]

        description = f"{job['description']}\n\n" if job["description"] else ""

        if job["healthReport"]:
            description += job["healthReport"][0]["description"]

        self.layout.add_column("col")
        self.layout.add_row("info", size=15)
        self.layout.add_row("nav", size=3)
        self.layout.add_row("details", min_size=20)
        self.layout.add_row("build_view", min_size=20)
        self.layout.show_row("build_view", False)

        self.layout.add_areas(
            info="col,info",
            nav="col,nav",
            build_view="col,build_view",
            details="col,details",
        )

        info = InfoWidget(title=name, renderable=description.strip())
        self.nav = JobNavView()
        self.details = JobDetailsWidget(path=self.path)

        self.layout.place(info=info)
        self.layout.place(nav=self.nav)
        self.layout.place(details=self.details)

        if self.job_has_parameters:
            self.build_with_params = BuildWithParametersView(job=job)
            self.layout.place(build_view=self.build_with_params)

    def send_message_for_button(self, button: str) -> None:
        """Helper method to send a button pressed message from the child widget.
        Args:
            button (str): The name of the button.
        """
        self.post_message_from_child_no_wait(ButtonPressed(self.nav.buttons[button]))

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "h":
            self.send_message_for_button("history")
        elif key == "b":
            self.send_message_for_button("build")

    async def handle_button_pressed(self, message: ButtonPressed):
        # reset previous current button toggle value

        if self.current_button:
            self.current_button.toggle = False

        # set new current button toggle value
        self.current_button = message.sender
        assert isinstance(self.current_button, ButtonWidget)
        self.current_button.toggle = True

        if message.sender.name != "build":
            self.layout.show_row("build_view", False)
            self.layout.show_row("details", True)

        if message.sender.name == "history":
            self.details.render_history_table()

        if message.sender.name == "build":
            if self.job_has_parameters:
                self.layout.show_row("build_view", True)
                self.layout.show_row("details", False)
                self.build_with_params.visible = True
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

                self.send_message_for_button("history")

        self.details.refresh()
        self.refresh(layout=True)
