import os
import sys

from textual.reactive import Reactive
from textual.app import App
from textual.widgets import ScrollView

from . import config
from .tree import JenkinsTree
from .views import JenkinsScrollView, JenkinsHomeView
from .widgets import JenkinsHeader, JenkinsFooter, JenkinsScrollBar

from .containers import Container


class JenkinsTUI(App):
    """This is the base class for Jenkins TUI."""

    chicken_mode_enabled: Reactive[bool] = Reactive(False)

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
        home_view = JenkinsHomeView()
        self.container = JenkinsScrollView(intial_view=home_view)
        self.container.vscroll = JenkinsScrollBar()
        await self.view.dock(self.container)


def run():
    """The entry point."""

    # set up di
    from . import widgets
    from . import views
    from . import tree

    conf = config.get_config()
    container = Container()
    container.config.from_dict(dict(conf))
    container.init_resources()
    container.wire(modules=[sys.modules[__name__], widgets, views, tree])

    # run the app
    log = os.getenv("JENKINSTUI_LOG")
    chicken = os.getenv("JENKINSTUI_DEVMODE")
    # JenkinsTUI.chicken_mode_enabled = chicken
    JenkinsTUI.run(title=config.app_name, log=log)


if __name__ == "__main__":
    """Stuff that runs when you call the package directly (python -m jenkins_tui.app)"""

    os.environ["JENKINSTUI_LOG"] = "textual.log"
    os.environ["JENKINSTUI_DEVMODE"] = "true"
    os.environ["JENKINSTUI_FEATURE_NAV"] = "true"
    run()
