from rich.table import Table
from textual.keys import Keys

UP = "\u2191"
DOWN = "\u2193"
LEFT = "\u2190"
RIGHT = "\u2192"


class HelpRenderable:
    shortcuts = {
        "global": {
            "back": Keys.Escape,
            "toggle help": "?",
            "quit": Keys.ControlC,
        },
        "navigation": {
            "navigate": f"{UP} {DOWN}",
            "toggle folder": f"{LEFT} {RIGHT}",
            "select": Keys.Enter,
        },
        "jobs": {
            "history": "h",
            "build": "b",
            "next page": f"{RIGHT}",
            "previous page": f"{LEFT}",
            "first page": "f",
            "last page": "l",
            "next row": f"{DOWN}",
            "previous row": f"{UP}",
        },
    }

    def __str__(self) -> str:
        return str(self.shortcuts)

    def __rich__(self) -> Table:
        table = Table(box=None, expand=False, show_footer=False, show_header=False)
        table.add_column(style="grey82")
        table.add_column(style="orange3 bold")
        for category, shortcuts in self.shortcuts.items():
            table.add_row(f"[green]{category}[/]")
            for action, shortcut in shortcuts.items():
                table.add_row(action, shortcut)
            else:
                table.add_row()

        return table
