import os
import requests
import sys
import toml

from . import config
from jenkins import Jenkins, JenkinsException
from typing import Union

from textual.app import App
from textual.views import GridView
from textual.widgets import ScrollView
from textual.reactive import Reactive

from .widgets.scroll_bar import ScrollBar
from .widgets.header import Header
from .widgets.footer import Footer
from .widgets.tree import JenkinsTree, JobClick
from .widgets.job_info import JobInfo
from .widgets.build_table import BuildTable

from dataclasses import dataclass


@dataclass
class ClientConfig:
    url: str
    username: str
    password: str


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    style: Reactive[str] = Reactive("")
    height: Union[Reactive[int], None] = Reactive(None)
    info_text: Reactive[str] = Reactive("")
    chicken_mode_enabled: Reactive[bool] = False
    _client: Jenkins = None
    _url: Reactive[str] = None

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

                _client = Jenkins(url=url, username=username, password=password)

                self.log("Validating client connection..")
                _client.get_nodes()
            return _client
        except JenkinsException as e:
            self.console.print(
                f"An error occured while creating the jenkins client instance:\n{e}"
            )
            sys.exit(1)
        except Exception as e:
            self.console.print(f"An unexpected error occured:\n{e}")
            sys.exit(1)

    def __custom_http_requst(self, url: str, method: str = "GET") -> requests.Response:
        """Send a http request via the Jenkins client.

        Args:
            url (str): Url of the request.
            method (str, optional): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            requests.Response: A requests.Response instance.
        """
        self.log(f"Sending custom request: {method}: {url}")
        request = requests.Request(method, url)
        response = self.__client.jenkins_request(request)
        response.raise_for_status()

        return response

    async def on_load(self) -> None:
        """Overrides on_load from App()"""

        self.__client = self.__get_client()

        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")
        await self.bind("r", "refresh", "Refresh")

    async def on_mount(self) -> None:
        """Overrides on_mount from App()"""

        # Dock header and footer
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")

        # Dock tree
        self.directory = JenkinsTree(client=self.__client, name="jenkins_tree")
        directory_scroll_view = ScrollView(self.directory)
        directory_scroll_view.vscroll = ScrollBar()
        await self.view.dock(
            directory_scroll_view, edge="left", size=40, name="sidebar"
        )

        # Dock container
        self.info = JobInfo()
        self.body = ScrollView()
        self.body.vscroll = ScrollBar()

        self.container = GridView()
        self.container.grid.add_column(name="col")
        self.container.grid.add_row(name="info", size=15)
        self.container.grid.add_row(name="jobs")
        self.container.grid.set_align("stretch", "center")

        areas = {"info": "col,info", "jobs": "col,jobs"}

        self.container.grid.add_areas(**areas)
        self.container.grid.place(info=self.info, jobs=self.body)

        await self.view.dock(self.container, edge="top")

    async def add_content(self):
        """Used to update the build info and job table widgets."""

        build_url = f"{self._url}/api/json?tree=displayName,description,healthReport[description],builds[number,status,timestamp,id,result,duration{{0,20}}]"
        response = self.__custom_http_requst(url=build_url).json()

        name = "chicken" if self.chicken_mode_enabled else response["displayName"]
        self.info_text = f"[bold]Name[/bold]\n{name}\n\n[bold]Description[/bold]\n{response['description']}"

        if response["healthReport"]:
            self.info_text += (
                f"\n\n[bold]Health[/bold]\n{response['healthReport'][0]['description']}"
            )

        builds = BuildTable(builds=response["builds"])

        await self.body.update(builds)
        self.body.refresh()

    async def handle_job_click(self, message: JobClick) -> None:
        """Used to process JobClick messages sent by the JenkinsTree instance.

        Args:
            message (JobClick): The message sent when a job node is clicked.
        """

        self._url = message.url
        await self.call_later(self.add_content)

    async def action_refresh(self) -> None:
        """Used to process refresh actions. Refreshes happen when you press R."""
        self.log("Refresh called")

        if self._url:
            self.log(f"Refreshing content for {self._url}")
            await self.add_content()
            self.log("Done refreshing content")

        self.view.refresh(layout=True)


def run():
    JenkinsTUI.run(title=config.app_name)


if __name__ == "__main__":
    JenkinsTUI.run(title=config.app_name, log="textual.log", chicken_mode_enabled=True)
