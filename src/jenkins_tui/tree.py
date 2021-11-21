from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import unquote

from dependency_injector.wiring import Container, Provide, inject
from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widgets import NodeID, TreeClick, TreeControl, TreeNode

from . import styles
from .client import Jenkins
from .containers import Container
from .views import JobView


@dataclass
class JobEntry:
    """Represents the data"""

    name: str
    url: str
    color: str
    type: str
    jobs: str | list[dict[str, str]]


class Tree(TreeControl[JobEntry]):

    current_node: JobEntry
    has_focus: Reactive[bool] = Reactive(False)

    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]) -> None:
        """Creates a directory tree struction from Jenkins jobs and builds.
        This class is a copy of textual.widgets.DirectoryTree with ammendments that allow it to be used with Jenkins Api responses.

        Args:
            client (Jenkins): A jenkins.Jenkins client instance.
            name (str): The name of the Tree instance.
        """
        data = JobEntry(name="root", url="", color="", type="root", jobs=[])
        name = self.__class__.__name__
        super().__init__(label="home", name=name, data=data)

        self.client = client
        self.color_map = {
            "aborted": "❌",
            "aborted_anime": "❌",
            "blue": "🔵",
            "blue_anime": "🔄",
            "disabled": "⭕",
            "grey": "⚪",
            "notbuilt": "⏳",
            "notbuilt_anime": "⏳",
            "red_anime": "🔄",
            "red": "🔴",
            "yellow": "🟡",
            "none": "🟣",
        }

        self.type_map = {
            "org.jenkinsci.plugins.workflow.job.WorkflowJob": "job",
            "com.cloudbees.hudson.plugins.folder.Folder": "folder",
            "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject": "multibranch",
            "hudson.model.FreeStyleProject": "freestyle",
        }

        self.root.tree.guide_style = styles.BLACK
        self.current_node = self.root.data
        self.padding = (0, 0)

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted.

        Args:
            event (events.Mount): A mount event.
        """
        await self.load_jobs(self.root)
        self.cursor = self.root.id
        self.show_cursor = True

    def on_focus(self) -> None:
        """Sets has_focus to true when the item is clicked."""
        self.has_focus = True

    def on_blur(self) -> None:
        """Sets has_focus to false when an item no longer has focus."""
        self.has_focus = False

    async def key_right(self, event: events.Key) -> None:
        cursor_node: TreeNode = self.nodes[self.cursor]
        event.stop()

        if cursor_node.data.type == "folder" or cursor_node.data.type == "multibranch":

            if not cursor_node.expanded:

                if not cursor_node.loaded:
                    await self.load_jobs(cursor_node)
                    await cursor_node.expand()
                else:
                    await cursor_node.toggle()

    async def key_left(self, event: events.Key) -> None:
        cursor_node: TreeNode = self.nodes[self.cursor]
        event.stop()

        if cursor_node.data.type == "folder" or cursor_node.data.type == "multibranch":
            if cursor_node.expanded:
                await cursor_node.toggle()
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
            label.stylize("underline")

        if is_cursor:
            style = "reverse" if self.has_focus else "on black"
            label.stylize(style)

        if type == "root":
            label.stylize(styles.GREY)
            icon = "🏠"  # "📂"

        elif type == "folder":
            label.stylize(styles.GREY)
            icon = "📂" if expanded else "📁"

        elif type == "multibranch":
            label.stylize(styles.GREY)
            icon = "🌱"

        else:
            label.stylize(styles.GREY)
            icon = self.color_map.get(node.data.color, "?")

        icon_label = Text(f"{icon} ", no_wrap=True, overflow="ellipsis") + label
        icon_label.apply_meta(meta)
        return icon_label

    async def watch_hover_node(self, hover_node: NodeID) -> None:
        """Configures styles for a node when hovered over by the mouse pointer."""
        for node in self.nodes.values():
            node.tree.guide_style = (
                styles.GREY if node.id == hover_node else styles.BLACK
            )
        self.refresh(layout=True)

    async def action_click_label(self, node_id: NodeID) -> None:
        """Overrides action_click_label from tree control and sets show cursor to True"""
        node = self.nodes[node_id]
        self.cursor = node.id
        self.cursor_line = self.find_cursor() or 0
        self.show_cursor = True
        await self.post_message(TreeClick(self, node))

    async def load_jobs(self, node: TreeNode[JobEntry]):
        """Load jobs for a tree node. If the current node is "root" then a call is made to Jenkins to retrieve a full list otherwise process jobs from the current node.

        Args:
            node (TreeNode[JobEntry]): [description]
        """
        jobs = []
        if node.data.type == "root":
            jobs = await self.client.get_jobs(recursive=True)
        else:
            jobs = node.data.jobs

        entry: dict[str, str]
        for entry in jobs:

            typeof = self.type_map.get(entry["_class"], "")
            clean_name = unquote(entry["name"])
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

    async def refresh_tree(self):
        self.root.tree.children.clear()
        await self.load_jobs(self.root)

    async def handle_tree_click(self, message: TreeClick[JobEntry]) -> None:
        """Handle messages that are sent when a tree item is clicked.

        Args:
            message (TreeClick[JobEntry]): A message that is sent when a tree item is clicked.
        """
        node_data = message.node.data
        if node_data.type == "job" or node_data.type == "freestyle":

            self.log("Handling JobClick message")

            async def _set():
                """Used to update the build info and job table widgets."""
                view = JobView(url=node_data.url)
                await self.app.container.update(view=view)

            # if the current node is the same as the clicked node then shouldn't do anything
            if node_data.name != self.current_node.name:
                self.current_node = node_data
                await self.call_later(_set)
            else:
                await self.app.set_focus(self.app.container.window)

        elif node_data.type == "root":
            self.log("Handling RootClick message")

            async def set() -> None:
                """Used to set the content of the homescren"""
                home = self.app.container.origin_view
                home.visible = True
                await self.app.container.update(view=home)

            if self.current_node.name != "root":
                self.current_node = node_data
                await self.call_later(set)

        else:
            if not message.node.loaded:
                await self.load_jobs(message.node)
                await message.node.expand()
            else:
                await message.node.toggle()
