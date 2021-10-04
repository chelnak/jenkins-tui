import rich.repr
from rich.style import Style

from jenkins_tui import config

from jenkins import Jenkins

from typing import Dict, List, Union
from urllib.parse import unquote

from rich.console import RenderableType
from rich.text import Text

from functools import lru_cache

from dataclasses import dataclass
from textual import events
from textual.reactive import Reactive
from textual.message import Message
from textual._types import MessageTarget
from textual.widgets import TreeControl, TreeClick, TreeNode, NodeID


@dataclass
class JobEntry:
    """Represents the data"""

    name: str
    url: str
    color: str
    type: str
    jobs: Union[str, List[Dict[str, str]]]


@rich.repr.auto
class JobClick(Message):
    def __init__(self, sender: MessageTarget, name: str, url: str) -> None:
        """Represents the message that is sent when a job node is clicked.

        Args:
            sender (MessageTarget): The class that sent the message.
            name (str): The name of the node.
            url (str): The url used for retrieving more information.
        """

        self.name = name
        self.url = url
        super().__init__(sender)


class JenkinsTree(TreeControl[JobEntry]):

    has_focus: Reactive[bool] = Reactive(False)

    def __init__(self, client: Jenkins, name: str) -> None:
        """Creates a directory tree struction from Jenkins jobs and builds.
        This class is a copy of textual.widgets.DirectoryTree with ammendments that allow it to be used with Jenkins Api responses.

        Args:
            client (Jenkins): A jenkins.Jenkins client instance.
            name (str): The name of the Tree instance.
        """
        data = JobEntry(name="root", url="", color="", type="root", jobs=[])
        super().__init__(label="pipelines", name=name, data=data)

        self.__styles = config.style_map[config.style]
        self.__client = client
        self.__color_map = {
            "aborted": "❌",
            "blue": "🔵",
            "blue_anime": "🔄",
            "disabled": "⭕",
            "grey": "⚪",
            "notbuilt": "⏳",
            "red_anime": "🔄",
            "red": "🔴",
            "yellow": "🟡",
            "none": "🟣",
        }

        self.__type_map = {
            "org.jenkinsci.plugins.workflow.job.WorkflowJob": "job",
            "com.cloudbees.hudson.plugins.folder.Folder": "folder",
            "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject": "multibranch",
        }

        self.root.tree.guide_style = self.__styles["tree_guide"]

    def on_focus(self) -> None:
        """Sets has_focus to true when the item is clicked."""

        self.has_focus = True

    def on_blur(self) -> None:
        """Sets has_focus to false when an item no longer has focus."""

        self.has_focus = False

    async def watch_hover_node(self, hover_node: NodeID) -> None:
        """Configures styles for a node when hovered over by the mouse pointer."""

        for node in self.nodes.values():
            node.tree.guide_style = (
                self.__styles["tree_guide_on_hover"]
                if node.id == hover_node
                else self.__styles["tree_guide"]
            )
        self.refresh(layout=True)

    def render_node(self, node: TreeNode[JobEntry]) -> RenderableType:
        """Renders a node in the tree.

        Args:
            node (TreeNode[JobEntry]): A node in the tree.

        Returns:
            RenderableType: A renderable object.
        """

        return self.render_tree_label(
            node,
            node.data.type,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
        )

    @lru_cache(maxsize=1024 * 32)
    def render_tree_label(
        self,
        node: TreeNode[JobEntry],
        type: str,
        expanded: bool,
        is_cursor: bool,
        is_hover: bool,
        has_focus: bool,
    ) -> RenderableType:
        """[summary]

        Args:
            node (TreeNode[JobEntry]): [description]
            type (str): [description]
            expanded (bool): [description]
            is_cursor (bool): [description]
            is_hover (bool): [description]
            has_focus (bool): [description]

        Returns:
            RenderableType: [description]
        """

        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }

        label = Text(node.label) if isinstance(node.label, str) else node.label

        if is_hover:
            label.stylize(self.__styles["node_on_hover"])

        if type == "folder":
            label.stylize(self.__styles["folder"])
            icon = "📂" if expanded else "📁"

        elif type == "root":
            label.stylize(self.__styles["root_node"])
            icon = "📂"

        elif type == "multibranch":
            label.stylize(self.__styles["multibranch_node"])
            icon = "🌱"

        else:
            label.stylize(self.__styles["node"])
            icon = self.__color_map.get(node.data.color, "?")

        icon_label = Text(f"{icon} ", no_wrap=True, overflow="ellipsis") + label
        icon_label.apply_meta(meta)
        return icon_label

    async def on_mount(self, event: events.Mount) -> None:
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """

        await self.load_jobs(self.root)

    async def load_jobs(self, node: TreeNode[JobEntry]):
        """Load jobs for a tree node. If the current node is "root" then a call is made to Jenkins to retrieve a full list otherwise process jobs from the current node.

        Args:
            node (TreeNode[JobEntry]): [description]
        """

        jobs = []
        if node.data.name == "root":
            jobs = self.__client.get_jobs()
        elif node.data.jobs:
            jobs = node.data.jobs

        entry: dict[str, str]
        for entry in jobs:

            typeof = self.__type_map.get(entry["_class"], "")
            clean_name = (
                "chicken"
                if getattr(self.app, "chicken_mode_enabled", None)
                else unquote(entry["name"])
            )
            parts = entry["url"].strip("/").split("/job/")
            full_name = "/".join(parts[1:])

            job = JobEntry(
                name=full_name,
                url=entry["url"],
                color=entry.get("color", "none"),
                type=typeof,
                jobs=entry.get("jobs", []),
            )

            await node.add(clean_name, job)

        node.loaded = True
        await node.expand()
        self.refresh(layout=True)

    async def handle_tree_click(self, message: TreeClick[JobEntry]) -> None:
        """Handle messages that are sent when a tree item is clicked.

        Args:
            message (TreeClick[JobEntry]): A message that is sent when a tree item is clicked.
        """
        node_data = message.node.data

        if node_data.type == "job":
            self.log("Emitting JobClick message")
            await self.emit(JobClick(self, node_data.name, node_data.url))
        else:
            if not message.node.loaded:
                await self.load_jobs(message.node)
                await message.node.expand()
            else:
                await message.node.toggle()
