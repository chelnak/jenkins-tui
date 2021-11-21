from dependency_injector import containers, providers

from .client import Jenkins


class Container(containers.DeclarativeContainer):
    """Defines the main container used for dependency injection."""

    config = providers.Configuration()

    client = providers.Factory(
        Jenkins, url=config.url, username=config.username, password=config.password
    )
