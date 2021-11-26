from __future__ import annotations

import os
from typing import Any, MutableMapping

import toml
from rich.console import Console
from validators import url

from . import styles
from .ask import Ask

"""
All of the good stuff. This is should be the main point for app configuration.
"""

# General
APP_NAME = "Jenkins"

CLI_HELP = """
jenkins-tui is a terminal based user interface for Jenkins!
"""


def set_config(path: str) -> MutableMapping[str, Any]:
    """Create a configuration file for the client.

    Args:
        path (str): Path to the configuration file.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    config = {}
    console = Console()
    ask = Ask()

    console.print(
        "It looks like this is the first time you are using this app.. lets add some configuration before we start :smiley:\n"
    )
    config["url"] = ask.question(f"[b][{styles.GREY}]url[/][/]", validation=url)
    config["username"] = ask.question(f"[b][{styles.GREY}]username[/][/]")
    config["password"] = ask.question(
        f"[b][{styles.GREY}]password[/][/]", password=True
    )

    with open(path, "w") as f:
        toml.dump(config, f)

    return toml.load(path)


def get_config(config: str | None = None) -> MutableMapping[str, Any]:
    """Retrieve or create configuration for the Jenkins client.

    Args:
        config (str | None): Path to the configuration file.

    Returns:
        MutableMapping[str, Any]: Configuration for the client.
    """

    if config and os.path.exists(config):
        client_config = toml.load(config)

    elif config and not os.path.exists(config):
        client_config = set_config(config)

    else:
        home = os.getenv("HOME")
        config_path = f"{home}/.jenkins-tui.toml"

        if not os.path.exists(config_path):
            client_config = set_config(config_path)
        else:
            client_config = toml.load(config_path)

    return client_config
