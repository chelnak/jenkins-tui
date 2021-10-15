from __future__ import annotations

from .base_view import JenkinsBaseView
from ..widgets import JenkinsJobInfo, JenkinsBuildQueue, JenkinsExecutorStatus


class JenkinsHomeView(JenkinsBaseView):
    """A view that contains widgets that are displayed on the home screen."""

    async def on_mount(self) -> None:
        """Actions that are executed when the widget is mounted."""

        self.layout.add_column("col", repeat=6)
        self.layout.add_row("info", size=10)
        self.layout.add_row("queue", min_size=10)
        self.layout.add_row("executor", min_size=10)

        self.layout.add_areas(
            info="col1-start|col6-end,info",
            queue="col1-start|col6-end,queue",
            executor="col1-start|col6-end,executor",
        )

        self.layout.place(info=JenkinsJobInfo())

        self.layout.place(queue=JenkinsBuildQueue(), executor=JenkinsExecutorStatus())
