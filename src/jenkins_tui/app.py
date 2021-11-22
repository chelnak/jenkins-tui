import os
import sys
from io import TextIOWrapper
from typing import Optional

import click
from click.types import File
from rich.text import Text
from textual.app import App
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widgets import Placeholder

from . import __version__, styles
from .config import APP_NAME, CLI_HELP, get_config
from .containers import Container
from .views import CustomScrollView, HomeView, SideBarView
from .widgets import (
    FlashWidget,
    HelpWidget,
    ScrollBarWidget,
    ShowFlashNotification,
    TextInputFieldWidget,
)


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    show_help = Reactive(False)
    # show_command_pallet = Reactive(False)

    async def on_load(self) -> None:
        """Overrides on_load from App()"""
        await self.bind("?", "toggle_help", "show help")
        await self.bind(Keys.Escape, "refocus_tree", show=False)
        await self.bind(Keys.ControlK, "toggle_command_pallet", show=False)

    async def watch_show_help(self, show_help: bool) -> None:
        self.help.visible = show_help

    async def action_toggle_help(self) -> None:
        self.show_help = not self.show_help

    # async def watch_show_command_pallet(self, show_command_pallet: bool) -> None:
    #     self.command_pallet.visible = show_command_pallet

    # async def action_toggle_command_pallet(self) -> None:
    #     self.show_command_pallet = not self.show_command_pallet

    #     if self.show_command_pallet:
    #         await self.app.set_focus(self.command_pallet)

    async def action_refocus_tree(self) -> None:
        """Actions that are executed when the history button is pressed."""
        self.show_help = False
        # self.show_command_pallet = False
        await self.side_bar.set_tree_focus()

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        # self.command_pallet = TextInputFieldWidget(
        #     name="search",
        #     title=Text("🔍 search"),
        #     border_style=styles.PURPLE,
        #     required=True,
        # )
        # self.command_pallet.visible = False
        # await self.view.dock(
        #     self.command_pallet, edge="top", size=3, name="command_pallet"
        # )

        self.side_bar = SideBarView()
        await self.view.dock(self.side_bar, edge="left", size=40, name="sidebar")

        # Dock content container
        self.container = CustomScrollView(
            intial_view=HomeView(), name="ContentScrollView"
        )
        self.container.vscroll = ScrollBarWidget()
        await self.view.dock(self.container)

        self.flash = FlashWidget()
        await self.view.dock(self.flash, edge="bottom", z=1)

        self.help = HelpWidget()
        self.help.visible = False

        await self.view.dock(self.help, edge="left", size=40, z=1)

    async def handle_show_flash_notification(self, message: ShowFlashNotification):
        self.log("Handling ShowFlashNotification message")
        await self.flash.update_flash_message(value=message.value, type=message.type)


@click.command(help=CLI_HELP)
@click.option(
    "--config",
    default=None,
    type=File(),
    help="Explicitly override the config that will be used by jenkins-tui.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode.",
)
@click.version_option(__version__)
def run(config: Optional[TextIOWrapper], debug: bool) -> None:
    """The entry point."""

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
            console.print(f"💥 It looks like there has been an error!\n\n {e}")


if __name__ == "__main__":
    """Stuff that runs when you call the package directly (python -m jenkins_tui.app)"""
    run()
