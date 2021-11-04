from __future__ import annotations

from dependency_injector.wiring import Provide, inject

from .base import BaseView
from ..widgets import SingleStatWidget
from ..client import Jenkins
from ..containers import Container


class StatsView(BaseView):
    @inject
    def __init__(self, client: Jenkins = Provide[Container.client]) -> None:
        """A view that can display a number of single stat widgets.

        Args:
            client (Jenkins): An instance of Jenkins.
        """
        self.client = client
        super().__init__()

    async def update_stats(self) -> None:
        """Updates the values for the child widgets."""
        self.log("Updating stats")

        queued_jobs = await self.client.get_queued_jobs()
        running_builds = await self.client.get_running_builds()

        self.stats["queued"].value = len(queued_jobs)
        self.stats["running"].value = len(running_builds)

        self.log("Done updating stats")

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.stats = {
            "queued": SingleStatWidget(name="queued"),
            "running": SingleStatWidget(name="running"),
        }

        for k, _ in self.stats.items():
            self.layout.add_column(f"col_{k}", size=30)

        self.layout.add_row("row", min_size=3)
        self.layout.set_align("center", "center")

        self.set_interval(10, self.update_stats)
        self.layout.place(*list(self.stats.values()))
        self.call_later(self.update_stats())
