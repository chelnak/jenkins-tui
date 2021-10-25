import os
import sys
from typing import Any, MutableMapping
import toml

from rich.console import Console
from textual.app import App
from textual.widgets import ScrollView

from . import config
from .views import JenkinsScrollView, JenkinsHomeView, JenkinsBuildView
from .widgets import JenkinsHeader, JenkinsFooter, JenkinsScrollBar, JenkinsTree
from .messages import JobClick

from .containers import Container


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    def __init__(
        self, title: str, log: str = None, chicken_mode_enabled: bool = False, **kwargs
    ):
        """Jenkins TUI

        Args:
            title (str): Title of the application.
            log (str, optional): Name of the log file that the app will write to. Defaults to None.
            chicken_mode_enabled (bool, optional): Enable super special chicken mode. Defaults to False.
        """

        super().__init__(title=title, log=log, log_verbosity=1, **kwargs)
        self.chicken_mode_enabled = chicken_mode_enabled
        self.current_node = "root"

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("r", "refresh_tree", "Refresh")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        # Dock header and footer
        await self.view.dock(JenkinsHeader(), edge="top")
        await self.view.dock(JenkinsFooter(), edge="bottom")

        # Dock tree container
        self.directory = JenkinsTree()
        self.tree_container = ScrollView(
            contents=self.directory,
            name="DirectoryScrollView",
        )
        self.tree_container.vscroll = JenkinsScrollBar()
        await self.view.dock(self.tree_container, edge="left", size=40, name="sidebar")

        # Dock content container
        self.container = JenkinsScrollView()
        await self.view.dock(self.container)

    # Message handlers
    async def handle_root_click(self) -> None:
        """Used to process RootClick messages sent by the JenkinsTree instance.

        Args:
            message (RootClick): The message sent when a the root node is clicked.
        """
        self.log("Handling RootClick message")

        async def set() -> None:
            """Used to set the content of the homescren"""
            view = JenkinsHomeView()
            await self.container.update(view=view)

        if self.current_node != "root":
            self.current_node = "root"
            await self.call_later(set)

    async def handle_job_click(self, message: JobClick) -> None:
        """Used to process JobClick messages sent by the JenkinsTree instance.

        Args:
            message (JobClick): The message sent when a job node is clicked.
        """

        self.log("Handling JobClick message")

        async def set() -> None:
            """Used to update the build info and job table widgets."""
            view = JenkinsBuildView(url=message.url)
            await self.container.update(view=view)

        if message.node_name != self.current_node:
            self.current_node = message.node_name
            await self.call_later(set)

    # Action handlers
    async def action_refresh_tree(self) -> None:
        """Used to process refresh actions. Refreshes happen when you press R."""
        self.log("Handling action refresh_tree")
        await self.directory.refresh_tree()


def get_config() -> MutableMapping[str, Any]:
    """Retrieve or create configuration for the Jenkins client.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    home = os.getenv("HOME")
    config_path = f"{home}/.jenkins-tui.toml"
    console = Console()
    if not os.path.exists(config_path):
        _config = {}
        console.print(
            "It looks like this is the first time you are using this app.. lets add some configuration before we start :smiley:\n"
        )
        _config["url"] = console.input("[b]url: [/]")
        _config["username"] = console.input("[b]username: [/]")
        _config["password"] = console.input("[b]password: [/]", password=True)

        with open(config_path, "w") as f:
            toml.dump(_config, f)

    client_config = toml.load(config_path)
    return client_config


def run():
    """The entry point."""

    # set up di
    from . import widgets
    from . import views

    conf = get_config()
    container = Container()
    container.config.from_dict(dict(conf))
    container.init_resources()
    container.wire(modules=[sys.modules[__name__], widgets, views])

    # run the app
    log = os.getenv("JENKINSTUI_LOG")
    chicken = os.getenv("JENKINSTUI_DEVMODE")
    JenkinsTUI.run(title=config.app_name, log=log, chicken_mode_enabled=chicken)


if __name__ == "__main__":
    """Stuff that runs when you call the package directly (python -m jenkins_tui.app)"""

    os.environ["JENKINSTUI_LOG"] = "textual.log"
    os.environ["JENKINSTUI_DEVMODE"] = "true"
    os.environ["JENKINSTUI_FEATURE_NAV"] = "true"
    run()
