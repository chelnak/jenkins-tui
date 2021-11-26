from __future__ import annotations

import sys

import click
from click.types import Path
from textual.app import App
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widgets import NodeID, TreeNode

from . import __version__
from .config import APP_NAME, CLI_HELP, get_config
from .containers import Container
from .views import CustomScrollView, HomeView, SideBarView
from .widgets import (
    FlashWidget,
    HelpWidget,
    NavWidget,
    ScrollBarWidget,
    SearchWidget,
    ShowFlashNotification,
)


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    search_node: Reactive[int] = Reactive(0)
    searchable_nodes: Reactive[dict[NodeID, TreeNode]] = Reactive({})
    show_help = Reactive(False)
    show_search = Reactive(False)
    nav_title: Reactive[str] = Reactive("")

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        await self.bind("?", "toggle_help", "show help")
        await self.bind(Keys.Escape, "refocus_tree", show=False)
        await self.bind(Keys.ControlK, "toggle_search", show=False)

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        self.side_bar = SideBarView()
        await self.view.dock(self.side_bar, edge="left", size=40, name="sidebar")

        self.nav = NavWidget()
        await self.view.dock(self.nav, edge="top", size=8, name="nav")

        self.search = SearchWidget()
        await self.view.dock(self.search, edge="top", size=3, name="search")

        self.container = CustomScrollView(
            intial_view=HomeView(), name="ContentScrollView"
        )
        self.container.vscroll = ScrollBarWidget()
        await self.view.dock(self.container)

        self.flash = FlashWidget()
        await self.view.dock(self.flash, edge="bottom", z=1)

        self.help = HelpWidget()
        await self.view.dock(self.help, edge="left", size=40, z=1)

    async def watch_show_help(self, show_help: bool) -> None:
        """Watch show_help and update widget visibility.

        Args:
            show_help (bool): Widget is shown if True and not shown if False.
        """

        self.help.visible = show_help

    async def watch_show_search(self, show_search: bool) -> None:
        """Watch show_search and update widget visibility.

        Args:
            show_search (bool): Widget is shown if True and not shown if False.
        """

        self.search.visible = show_search

    async def action_toggle_help(self) -> None:
        """Toggle the help widget."""

        self.show_help = not self.show_help

        if self.show_help:
            await self.app.set_focus(self.help)
        else:
            await self.side_bar.set_tree_focus()

    async def action_toggle_search(self) -> None:
        """Toggle the search widget"""

        self.show_search = not self.show_search

        if self.show_search:
            await self.app.set_focus(self.search)
        else:
            await self.side_bar.set_tree_focus()
            self.search.value = ""

    async def action_refocus_tree(self) -> None:
        """Refocus the tree."""

        if self.side_bar.tree_has_focus:
            await self.side_bar.reset_tree()
        else:
            self.show_help = False
            self.show_search = False
            self.search.value = ""

            await self.side_bar.set_tree_focus()

    async def handle_show_flash_notification(
        self, message: ShowFlashNotification
    ) -> None:
        """Handle a ShowFlashNotification message.

        Args:
            message (ShowFlashNotification): The message to handle.
        """

        self.log("Handling ShowFlashNotification message")
        await self.flash.update_flash_message(value=message.value, type=message.type)


@click.command(help=CLI_HELP)
@click.option(
    "--config",
    default=None,
    envvar="JENKINS_TUI_CONFIG",
    type=Path(file_okay=True, dir_okay=False, exists=False, resolve_path=True),
    help="Explicitly override the config that will be used by jenkins-tui.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.version_option(__version__)
def run(config: str | None, debug: bool) -> None:
    """The entry point.

    Args:
        config (str | None): The config file to use.
        debug (bool): Enable debug mode.
    """

    # set up di
    from . import tree, views, widgets

    conf = get_config(config=config)
    container = Container()
    container.config.from_dict(dict(conf))
    container.init_resources()
    container.wire(modules=[sys.modules[__name__], widgets, views, tree])

    # run the app
    if debug:
        JenkinsTUI.run(title=APP_NAME, log="jenkins_tui.log")
    else:
        try:
            JenkinsTUI.run(title=APP_NAME)

        except Exception as e:
            from rich.console import Console

            console = Console()
            console.print(
                f"💥 It looks like there has been an error. For more information use the --debug option!"
            )


if __name__ == "__main__":
    """Stuff that runs when you call the package directly (python -m jenkins_tui.app)"""
    run()
