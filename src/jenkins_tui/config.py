import os
import toml
from rich.console import Console
from typing import Any, MutableMapping

"""
All of the good stuff. This is should be the main point for app configuration.
"""

# General
app_name = "Jenkins"

# Styling
style = "clean"
style_map = {
    "common": {
        "orange": "orange3",
        "green": "green",
        "grey": "grey82",
        "purple": "medium_purple4",
    },
    "clean": {
        "grey": "grey82",
        "root_node": "grey82",
        "folder": "grey82",
        "node": "grey82",
        "node_on_hover": "underline",
        "multibranch_node": "grey82",
        "tree_guide": "black",
        "tree_guide_on_hover": "white",
        "tree_on_cursor": "reverse",
        "scroll_bar_foreground": "#6e6d6d",
        "scroll_bar_grabbed_foreground": "#9c9a9a",
        "scroll_bar_background": "#444444",
        "scroll_bar_background_on_hover": "#444444",
        "footer_style": "white on #444444",
    },
}


def get_config() -> MutableMapping[str, Any]:
    """Retrieve or create configuration for the Jenkins client.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    home = os.getenv("HOME")
    config_path = f"{home}/.jenkins-tui.toml"
    console = Console()
    if not os.path.exists(config_path):
        _config = {}
        console.print(
            "It looks like this is the first time you are using this app.. lets add some configuration before we start :smiley:\n"
        )
        _config["url"] = console.input("[b]url: [/]")
        _config["username"] = console.input("[b]username: [/]")
        _config["password"] = console.input("[b]password: [/]", password=True)

        with open(config_path, "w") as f:
            toml.dump(_config, f)

    client_config = toml.load(config_path)
    return client_config
