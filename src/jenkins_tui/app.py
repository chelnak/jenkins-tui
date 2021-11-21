import os
import sys
from io import TextIOWrapper
from typing import Optional

import click
from click.types import File
from textual.app import App
from textual.keys import Keys
from textual.reactive import Reactive

from . import __version__
from .config import APP_NAME, CLI_HELP, get_config
from .containers import Container
from .views import CustomScrollView, HomeView, SideBarView
from .widgets import FlashWidget, HelpWidget, ScrollBarWidget, ShowFlashNotification


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    show_help = Reactive(False)
    chicken_mode_enabled: Reactive[bool] = Reactive(False)

    async def on_load(self) -> None:
        """Overrides on_load from App()"""
        await self.bind("?", "toggle_help", "show help")
        await self.bind(Keys.Escape, "refocus_tree", show=False)

    async def watch_show_help(self, show_help: bool) -> None:
        self.help.visible = show_help

    async def action_toggle_help(self) -> None:
        self.show_help = not self.show_help

    async def action_refocus_tree(self) -> None:
        """Actions that are executed when the history button is pressed."""
        self.log("action_history")
        self.show_help = False
        await self.side_bar.set_tree_focus()

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

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
@click.version_option(__version__)
def run(config: Optional[TextIOWrapper]) -> None:
    """The entry point."""

    # set up di
    from . import tree, views, widgets

    conf = get_config(config=config)
    container = Container()
    container.config.from_dict(dict(conf))
    container.init_resources()
    container.wire(modules=[sys.modules[__name__], widgets, views, tree])

    # run the app
    os.environ["JENKINSTUI_LOG"] = "textual.log"
    log = os.getenv("JENKINSTUI_LOG")

    try:
        JenkinsTUI.run(title=APP_NAME, log=log)
    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"💥 It looks like there has been an error!\n\n {e}")


if __name__ == "__main__":
    """Stuff that runs when you call the package directly (python -m jenkins_tui.app)"""

    os.environ["JENKINSTUI_LOG"] = "textual.log"
    os.environ["JENKINSTUI_DEVMODE"] = "true"
    os.environ["JENKINSTUI_FEATURE_NAV"] = "true"
    run()
