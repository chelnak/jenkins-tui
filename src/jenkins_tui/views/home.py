from __future__ import annotations

import re

from dependency_injector.wiring import Provide, inject
from rich.style import Style
from rich.text import Text

from .. import __version__, styles
from ..client import Jenkins
from ..containers import Container
from ..widgets import ExecutorStatusWidget, NavWidget, TextWidget
from .base import BaseView


class HomeView(BaseView):
    """A view that contains widgets that are displayed on the home screen."""

    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]):
        """A view that contains widgets that are displayed on the home screen.

        Args:
            client (Jenkins, optional): An injected Jenkins http client instance. Defaults to Provide[Container.client].
        """
        super().__init__()
        self.client = client

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.layout.add_column("col")
        self.layout.add_row("nav", size=8)
        self.layout.add_row("info", size=3)
        self.layout.add_row("executor", min_size=25)

        self.layout.add_areas(
            nav="col,nav",
            info="col,info",
            executor="col,executor",
        )

        server_address = Text(
            self.client.url, style=Style(link=self.client.url), overflow="ellipsis"
        )
        server_version = self.client.version
        client_version = __version__

        HTML = re.compile(r"<[^>]+>")
        clean_description = HTML.sub("", self.client.description)

        title = Text.assemble(
            *[
                Text.from_markup(f"[{styles.GREY}][bold]{clean_description}[/][/]\n"),
                Text.from_markup(
                    f"server: [{styles.GREEN}]{server_version}[/] [{styles.ORANGE}]⚡[/]client: [{styles.GREEN}]{client_version}[/]"
                ),
            ],
            justify="center",
        )

        self.layout.place(
            nav=NavWidget(title=title),
        )

        self.layout.place(
            info=TextWidget(
                text=f"Welcome to Jenkins TUI! 🚀\nYour instance url is: {server_address}",
            )
        )
        self.layout.place(executor=ExecutorStatusWidget())
