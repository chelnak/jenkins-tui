from __future__ import annotations

import os

from urllib.parse import urlparse
from dependency_injector.wiring import Container, Provide, inject
from rich.text import Text

from ..client import Jenkins
from ..widgets import JenkinsJobInfo, JenkinsBuildTable, JenkinsButton
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
        self.layout.add_column("col", repeat=6)
        self.layout.add_row("info", size=10)

        if nav_feature:
            self.layout.add_row("nav", size=3)

        self.layout.add_row("body", min_size=25)

        self.layout.add_areas(
            info="col1-start|col6-end,info",
            nav="col1-start|col6-end,nav",
            body="col1-start|col6-end,body",
        )

        info = JenkinsJobInfo(title=name, text=info_text)
        builds = JenkinsBuildTable(url=self.url)

        self.layout.place(info=info)

        def make_button(text: str):
            return JenkinsButton(label=Text(text))

        if nav_feature:
            buttons = [make_button(b) for b in ["status", "changes", "build"]]
            self.layout.place(*buttons)

        self.layout.place(body=builds)
