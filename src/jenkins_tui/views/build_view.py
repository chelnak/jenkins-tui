from __future__ import annotations

import os

from urllib.parse import urlparse
from dependency_injector.wiring import Container, Provide, inject
from rich.text import Text
from textual.layouts.grid import GridLayout
from textual.widget import Widget

from textual.widgets import ButtonPressed

from ..client import Jenkins
from ..widgets import (
    JenkinsJobInfo,
    JenkinsBuildTable,
    JenkinsButton,
    JenkinsBuildChangesTable,
)
from ..containers import Container
from .base_view import JenkinsBaseView


class JenkinsBuildView(JenkinsBaseView):
    """A view that contains widgets that display build information."""

    @inject
    def __init__(self, url: str, client: Jenkins = Provide[Container.client]) -> None:
        """A view that contains widgets that display build information.

        Args:
            url (str): The url of the current job.
            client (Jenkins, optional): An injected Jenkins http client instance. Defaults to Provide[Container.client].
        """
        super().__init__()
        self.url = url
        self.path = urlparse(url).path
        self.chicken_mode_enabled = getattr(self.app, "chicken_mode_enabled", False)
        self.client = client
        self.buttons: dict[str, JenkinsButton] = {}
        self.current_button: JenkinsButton | None = None
        self.current_widget: Widget | None = None

    async def update(self, widget: Widget) -> None:
        """Update the content area of the grid view that backs ScrollView.

        Args:
            view (View): The view that will replace the current one assigned to the content area.
        """
        assert isinstance(self.layout, GridLayout)
        widgets = self.layout.widgets

        del widgets[self.current_widget]
        self.current_widget = widget
        self.layout.place(body=widget)

        await self.refresh_layout()

    async def handle_button_pressed(self, message: ButtonPressed):
        # reset previous current button toggle value
        if self.current_button:
            self.current_button.toggle = False

        # set new current button toggle value
        self.current_button = message.sender
        assert isinstance(self.current_button, JenkinsButton)
        self.current_button.toggle = True

        if message.sender.name == "changes":
            await self.update(JenkinsBuildChangesTable(self.url))

        await self.refresh_layout()

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        build_info = await self.client.get_info_for_job(path=self.path)

        name = "chicken" if self.chicken_mode_enabled else build_info["displayName"]
        lorum = "Chicken chicken chicken chick chick, chicken chicken chick. Chick chicken chicken chick. Chicken chicken chicken chick, egg chicken chicken. Chicken."
        description = lorum if self.chicken_mode_enabled else build_info["description"]

        info_text = f"[bold]description[/bold]\n{description}"

        if build_info["healthReport"]:
            info_text += f"\n\n[bold]health[/bold]\n{build_info['healthReport'][0]['description']}"

        # narly feature flag
        nav_feature = os.environ.get("JENKINSTUI_FEATURE_NAV")
        self.layout.add_column("col", repeat=7)
        self.layout.add_row("info", size=10)

        if nav_feature:
            self.layout.add_row("nav", size=3)

        self.layout.add_row("body", min_size=25)

        self.layout.add_areas(
            info="col1-start|col7-end,info",
            status_btn="col3,nav",
            changes_btn="col4,nav",
            build_btn="col5, nav",
            body="col1-start|col7-end,body",
        )

        info = JenkinsJobInfo(title=name, text=info_text)
        builds = JenkinsBuildTable(url=self.url)

        self.layout.place(info=info)

        def make_button(text: str):

            label = Text(text=text)
            label.apply_meta({"@click": f"click_label({text})", "button": text})
            button = JenkinsButton(label=Text(text))
            self.buttons[text] = button
            return button

        if nav_feature:

            status_btn = make_button("status")
            self.layout.place(status_btn=status_btn)

            changes_btn = make_button("changes")
            self.layout.place(changes_btn=changes_btn)

            build_btn = make_button("build")
            self.layout.place(build_btn=build_btn)

            # we always land on the status page so toggle the button
            status_btn.toggle = True
            self.current_button = status_btn

        # also set the current widget
        self.current_widget = builds
        self.layout.place(body=builds)
