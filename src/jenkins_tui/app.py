from io import TextIOWrapper
import os
import sys
from typing import Optional
import click
from click.types import File
from textual.reactive import Reactive
from textual.app import App

from . import __version__
from .config import CLI_HELP, get_config, APP_NAME
from .views import CustomScrollView, HomeView, SideBarView
from .widgets import (
    ScrollBarWidget,
    FlashWidget,
    ShowFlashNotification,
)
from .containers import Container


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    chicken_mode_enabled: Reactive[bool] = Reactive(False)

    async def on_load(self) -> None:
        """Overrides on_load from App()"""
        await self.bind("r", "refresh_tree", "Refresh")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        await self.view.dock(SideBarView(), edge="left", size=40, name="sidebar")

        # Dock content container
        self.container = CustomScrollView(
            intial_view=HomeView(), name="ContentScrollView"
        )
        self.container.vscroll = ScrollBarWidget()
        await self.view.dock(self.container)

        self.flash = FlashWidget()
        await self.view.dock(self.flash, edge="bottom", z=1)

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
    from . import widgets
    from . import views
    from . import tree

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
