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
from ..widgets import ShowFlashNotification


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
        self.chicken_mode_enabled = getattr(self.app, "chicken_mode_enabled", False)
        self.client = client
        self.buttons: dict[str, ButtonWidget] = {}
        self.job_has_parameters: bool = False

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        job = await self.client.get_job(path=self.path)

        name = "chicken" if self.chicken_mode_enabled else job["displayName"]
        lorum = "Chicken chicken chicken chick chick, chicken chicken chick. Chick chicken chicken chick. Chicken chicken chicken chick, egg chicken chicken. Chicken."
        description = lorum if self.chicken_mode_enabled else job["description"]

        info_text = f"{description}"

        if job["healthReport"]:
            info_text += (
                f"\n\n[bold]health[/bold]\n{job['healthReport'][0]['description']}"
            )

        self.layout.add_column("col")
        self.layout.add_row("info", size=10)
        self.layout.add_row("nav", size=3)
        self.layout.add_row("details", min_size=25)

        self.layout.add_row("build_view", min_size=25)
        self.layout.show_row("build_view", False)

        self.layout.add_areas(
            info="col,info",
            nav="col,nav",
            build_view="col,build_view",
            details="col,details",
        )

        info = InfoWidget(title=name, renderable=info_text)
        self.nav = JobNavView()
        self.builds = JobDetailsWidget(job=job)

        self.layout.place(info=info)
        self.layout.place(nav=self.nav)
        self.layout.place(details=self.builds)

        if job["property"][0].get("parameterDefinitions"):
            self.job_has_parameters = True
            self.build_with_params = BuildWithParametersView(job=job)
            self.layout.place(build_view=self.build_with_params)

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "h":
            self.log("history KEY")

            self.post_message_from_child_no_wait(
                ButtonPressed(self.nav.buttons["history"])
            )
        elif key == "c":
            self.log("changes KEY")
            self.post_message_from_child_no_wait(
                ButtonPressed(self.nav.buttons["changes"])
            )
        elif key == "b":
            self.log("build KEY")
            self.post_message_from_child_no_wait(
                ButtonPressed(self.nav.buttons["build"])
            )

    async def handle_button_pressed(self, message: ButtonPressed):
        # reset previous current button toggle value
        self.log(f"button pressed {message.name}")
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
            self.log("history")
            self.builds.render_history_table()

        if message.sender.name == "changes":
            self.log("changes")
            self.builds.render_changes_table()

        if message.sender.name == "build":
            self.log("build")
            if self.job_has_parameters:
                self.layout.show_row("build_view", True)
                self.layout.show_row("details", False)
                self.build_with_params.visible = True
            else:
                self.log("Job has no parameters")

                await self.client.build(path=self.path)
                self.log("build started")

                self.post_message_from_child_no_wait(
                    ShowFlashNotification(self, value="Build scheduled ✅")
                )

                self.post_message_from_child_no_wait(
                    ButtonPressed(self.nav.buttons["history"])
                )

        self.refresh(layout=True)
