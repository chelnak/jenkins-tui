import os
import sys
import toml

from . import config
from jenkins import Jenkins, JenkinsException
from typing import Dict, List, Union

from textual.app import App
from textual.widgets import ScrollView
from textual.reactive import Reactive

from .views.window_view import WindowView
from .widgets.scroll_bar import ScrollBar
from .widgets.header import Header
from .widgets.footer import Footer
from .widgets.tree import JenkinsTree, JobClick, RootClick
from .widgets.job_info import JobInfo
from .widgets.build_table import BuildTable
from .widgets.executor_status import ExecutorStatus
from .widgets.build_queue import BuildQueue

from dataclasses import dataclass

from .jenkins_http import ExtendedJenkinsClient


@dataclass
class ClientConfig:
    """Represents Jenkins client configuration."""

    url: str
    username: str
    password: str


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    style: Reactive[str] = Reactive("")
    height: Union[Reactive[int], None] = Reactive(None)
    info_title: Reactive[str] = Reactive("")
    info_message: Reactive[str] = Reactive("")

    current_node: Reactive[str] = Reactive("root")

    running_builds: Reactive[List[Dict[str, str]]] = Reactive("")
    queued_builds: Reactive[List[Dict[str, str]]] = Reactive("")

    current_job_url: Reactive[str] = Reactive("")
    current_job_builds: Reactive[str] = Reactive("")

    chicken_mode_enabled: Reactive[bool] = False
    client: ExtendedJenkinsClient

    def __init__(
        self, title: str, log: str = None, chicken_mode_enabled: bool = False, **kwargs
    ):
        """Jenkins TUI

        Args:
            title (str): Title of the application.
            log (str, optional): Name of the log file that the app will write to. Defaults to None.
            chicken_mode_enabled (bool, optional): Enable super special chicken mode. Defaults to False.
        """

        self.chicken_mode_enabled = chicken_mode_enabled

        self.posible_areas = {
            "info": "col,info",
            "builds": "col,builds",
            "executor": "col,executor",
            "queue": "col,queue",
        }

        super().__init__(title=title, log=log)

    def __get_client(self) -> Jenkins:
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

                _client = ExtendedJenkinsClient(
                    url=url, username=username, password=password
                )

                self.log("Validating client connection..")
                _client.test_connection(sender=self)
            return _client
        except JenkinsException as e:
            self.console.print(
                f"An error occured while creating the jenkins client instance:\n{e}"
            )
            sys.exit(1)
        except Exception as e:
            self.console.print(f"An unexpected error occured:\n{e}")
            sys.exit(1)

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        self.client = self.__get_client()

        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("r", "refresh_tree", "Refresh")
        await self.bind("q", "quit", "Quit")

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        # Dock header and footer

        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Dock tree
        directory = JenkinsTree(client=self.client, name="JenkinsTreeWidget")
        self.directory_scroll_view = ScrollView(
            contents=directory, name="DirectoryScrollView"
        )
        self.directory_scroll_view.vscroll = ScrollBar()
        await self.view.dock(
            self.directory_scroll_view, edge="left", size=40, name="sidebar"
        )

        # Dock container
        # This is the main container that holds our info widget and the body
        self.info = JobInfo()
        self.build_queue = BuildQueue(client=self.client)
        self.executor_status = ExecutorStatus(client=self.client)

        self.container = WindowView()
        await self.container.dock(*[self.info, self.build_queue, self.executor_status])

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

            self.info_title = ""
            self.info_message = ""

            await self.container.update(
                self.info, self.build_queue, self.executor_status
            )

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
            build_url = f"{message.url}/api/json?tree=displayName,description,healthReport[description]"
            r = await self.client.custom_async_http_requst(sender=self, url=build_url)
            response = r.json()

            name = "chicken" if self.chicken_mode_enabled else response["displayName"]

            self.info_title = name
            self.info_message = f"[bold]description[/bold]\n{response['description']}"

            if response["healthReport"]:
                self.info_message += f"\n\n[bold]health[/bold]\n{response['healthReport'][0]['description']}"

            builds = BuildTable(client=self.client, url=message.url)

            await self.container.update(self.info, builds)

        if message.node_name != self.current_node:
            self.current_node = message.node_name
            await self.call_later(set_job)

    # Action handlers
    async def action_refresh_tree(self) -> None:
        """Used to process refresh actions. Refreshes happen when you press R."""
        self.log("Handling action refresh_tree")

        directory = JenkinsTree(client=self.client, name="JenkinsTreeWidget")
        await self.directory_scroll_view.update(directory)
        self.directory_scroll_view.refresh(layout=True)


def run():
    JenkinsTUI.run(title=config.app_name)


if __name__ == "__main__":
    JenkinsTUI.run(title=config.app_name, log="textual.log", chicken_mode_enabled=False)
