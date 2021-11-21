import os
from io import TextIOWrapper
from typing import Any, MutableMapping, Optional

import toml
from rich.console import Console

"""
All of the good stuff. This is should be the main point for app configuration.
"""

# General
APP_NAME = "Jenkins"

CLI_HELP = """
jenkins-tui is a terminal based user interface for Jenkins!
"""


def get_config(config: Optional[TextIOWrapper] = None) -> MutableMapping[str, Any]:
    """Retrieve or create configuration for the Jenkins client.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    if config:
        client_config = toml.load(config)
    else:
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
