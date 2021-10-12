import os
import sys
from typing import List
from urllib.parse import urlparse
from textual.widget import Widget
import toml

from textual.app import App
from textual.events import Mount
from textual.widgets import ScrollView


from . import config
from .client import Jenkins
from .views import TestScrollView
from .widgets import (
    Header,
    Footer,
    ScrollBar,
    JenkinsTree,
    JobClick,
    RootClick,
    JobInfo,
    ExecutorStatus,
    BuildQueue,
    BuildTable,
)

from dataclasses import dataclass


@dataclass
class ClientConfig:
    """Represents Jenkins client configuration."""

    url: str
    username: str
    password: str


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

    def _get_client(self) -> Jenkins:
        """Gets an instance of jenkins.Jenkins. Arguments are read from config. If the config doesn't exist, the user is prompted with some questions.

        Returns:
            Jenkins: An instance of jenkins.Jenkins
        """

        try:
            home = os.getenv("HOME")
            config_path = f"{home}/.jenkins-tui.toml"

            if not os.path.exists(config_path):
                _config = {}
                self.console.print(
                    "It looks like this is the first time you are using this app.. lets add some configuration before we start :smiley:\n"
                )
                _config["url"] = self.console.input("[b]url: [/]")
                _config["username"] = self.console.input("[b]username: [/]")
                _config["password"] = self.console.input(
                    "[b]password: [/]", password=True
                )

                with open(config_path, "w") as f:
                    toml.dump(_config, f)

            client_config = ClientConfig(**toml.load(config_path))

            with self.console.status("Loading jenkins...") as status:

                url = client_config.url
                username = client_config.username
                password = client_config.password

                _client = Jenkins(url=url, username=username, password=password)
            return _client
        except Exception as e:
            self.console.print(
                f"An error occured while creating the jenkins client instance:\n{e}"
            )
            sys.exit(1)
        except Exception as e:
            self.console.print(f"An unexpected error occured:\n{e}")
            sys.exit(1)

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        self.client = self._get_client()

        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("r", "refresh_tree", "Refresh")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: Mount) -> None:
        """Overrides on_mount from App()"""

        # Dock header and footer
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Dock tree
        directory = JenkinsTree(client=self.client, name="JenkinsTreeWidget")

        self.tree_container = ScrollView(
            contents=directory,
            name="DirectoryScrollView",
        )
        self.tree_container.vscroll = ScrollBar()
        await self.view.dock(self.tree_container, edge="left", size=40, name="sidebar")

        # Dock container
        # This is the main container that holds our info widget and the body
        self.info = JobInfo()
        self.build_queue = BuildQueue(client=self.client)
        self.executor_status = ExecutorStatus(client=self.client)

        widgets = [self.info, self.build_queue, self.executor_status]
        self.container = TestScrollView(contents=widgets)
        self.container.vscroll = ScrollBar()

        await self.view.dock(self.container)

    # Message handlers
    async def handle_root_click(self, message: RootClick) -> None:
        """Used to process RootClick messages sent by the JenkinsTree instance.

        Args:
            message (RootClick): The message sent when a the root node is clicked.
        """
        self.log("Handling RootClick message")

        async def set_home() -> None:
            """Used to set the content of the homescren"""

            widgets = [self.info, self.build_queue, self.executor_status]
            await self.container.window.update(widgets=widgets)

        if self.current_node != "root":
            self.current_node = "root"
            await self.call_later(set_home)

    async def handle_job_click(self, message: JobClick) -> None:
        """Used to process JobClick messages sent by the JenkinsTree instance.

        Args:
            message (JobClick): The message sent when a job node is clicked.
        """

        self.log("Handling JobClick message")

        async def set_job() -> None:
            """Used to update the build info and job table widgets."""

            # Populate BuildInfo widget
            url = urlparse(message.url)
            build_info = await self.client.get_info_for_job(path=url.path)

            name = "chicken" if self.chicken_mode_enabled else build_info["displayName"]
            lorum = "Chicken chicken chicken chick chick, chicken chicken chick. Chick chicken chicken chick. Chicken chicken chicken chick, egg chicken chicken. Chicken."
            description = (
                lorum if self.chicken_mode_enabled else build_info["description"]
            )

            info_text = f"[bold]description[/bold]\n{description}"

            if build_info["healthReport"]:
                info_text += f"\n\n[bold]health[/bold]\n{build_info['healthReport'][0]['description']}"

            info = JobInfo(title=name, text=info_text)
            builds = BuildTable(client=self.client, url=message.url)

            widgets: List[Widget] = [info, builds]
            await self.container.update(widgets=widgets)
            await self.container.refresh_layout()

        if message.node_name != self.current_node:
            self.current_node = message.node_name
            await self.call_later(set_job)

    # Action handlers
    async def action_refresh_tree(self) -> None:
        """Used to process refresh actions. Refreshes happen when you press R."""
        self.log("Handling action refresh_tree")

        directory = JenkinsTree(client=self.client, name="JenkinsTreeWidget")
        await self.tree_container.update(directory)
        self.tree_container.refresh(layout=True)


def run():
    JenkinsTUI.run(title=config.app_name)


if __name__ == "__main__":
    JenkinsTUI.run(title=config.app_name, log="textual.log", chicken_mode_enabled=False)
