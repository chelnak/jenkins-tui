from rich.console import RenderableType
from rich.panel import Panel

from textual.reactive import Reactive
from textual.widgets import Button
from textual.widgets._button import ButtonRenderable


class JenkinsButton(Button):

    mouse_over = Reactive(False)

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    def render(self) -> RenderableType:
        style = "on red" if self.mouse_over else self.button_style
        panel_content = ButtonRenderable(self.label, style=None)
        return Panel(panel_content, style=style, expand=True)
