from __future__ import annotations

import re

from dependency_injector.wiring import Provide, inject

from rich.console import Group
from rich.text import Text
from rich.style import Style

from .base import BaseView
from ..widgets import ExecutorStatusWidget, InfoWidget
from ..client import Jenkins
from ..containers import Container
from .. import __version__


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
        self.layout.add_row("info", size=10)
        self.layout.add_row("executor", min_size=25)

        self.layout.add_areas(
            info="col,info",
            executor="col,executor",
        )

        server_address = Text(
            self.client.url, style=Style(link=self.client.url), overflow="ellipsis"
        )
        server_version = self.client.version
        client_version = __version__

        render_group = Group(
            *[
                f"[bold]server:[/] {server_address}",
                f"[bold]server version:[/] {server_version}",
                f"[bold]client version:[/] {client_version}",
            ]
        )

        HTML = re.compile(r"<[^>]+>")
        clean_description = HTML.sub("", self.client.description)

        title = Text.assemble(
            *[
                Text.from_markup(f"[grey82][bold]{clean_description}[/][/]\n"),
                Text.from_markup(
                    f"server: [green]{server_version}[/] [orange3]⚡[/]client: [green]{client_version}[/]"
                ),
            ],
            justify="center",
        )
        self.layout.place(
            info=InfoWidget(
                title=title,
                renderable=f"Welcome to Jenkins TUI! 🚀\nYour instance url is: {server_address}",
            )
        )
        self.layout.place(executor=ExecutorStatusWidget())
