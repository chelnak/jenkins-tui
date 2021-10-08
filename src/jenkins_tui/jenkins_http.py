import httpx
from typing import Any, Dict, List
from textual.message_pump import MessagePump
from jenkins import Jenkins


class ExtendedJenkinsClient(Jenkins):
    """A class that extends the Jenkins client class."""

    def custom_http_requst(
        self, sender: MessagePump, url: str, method: str = "GET"
    ) -> httpx.Response:
        """Send a http request via the Jenkins client.

        Args:
            url (str): Url of the request.
            method (str, optional): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            httpx.Response: A requests.Response instance.
        """
        sender.log(
            f"Sending custom request from {sender.__class__.__name__}: {method}: {url}"
        )

        with httpx.Client() as client:
            auth = self._auths[0][1]
            response = client.request(method="GET", url=url, auth=auth)
            response.raise_for_status()
            return response

    async def custom_async_http_requst(
        self, sender: MessagePump, url: str, method: str = "GET"
    ) -> httpx.Response:
        """Send a http request via the Jenkins client.

        Args:
            url (str): Url of the request.
            method (str, optional): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            requests.Response: A requests.Response instance.
        """
        sender.log(
            f"Sending custom async request from {sender.__class__.__name__}: {method}: {url}"
        )

        async with httpx.AsyncClient() as client:
            auth = self._auths[0][1]
            response = await client.request(method=method, url=url, auth=auth)
            response.raise_for_status()
            return response

    def test_connection(self, sender: MessagePump) -> bool:
        """Test the connection to the Jenkins server

        Args:
            sender (MessagePump): The class that has sent the request.

        Returns:
            bool: True if the connection is valid.
        """
        _ = self.custom_http_requst(sender=sender, url=f"{self.server}/api/json")
        return True

    async def get_nodes(self, sender: MessagePump) -> List[Dict[Any, Any]]:
        """Get a list of nodes from the server

        Args:
            sender (MessagePump): The class that has sent the request.

        Returns:
            List[Dict[Any, Any]]: A list of node dicts.
        """
        url = f"{self.server}computer/api/json?tree=*,computer[*,executors[*,currentExecutable[*]]]"
        response = await self.custom_async_http_requst(sender=sender, url=url)
        return response.json()["computer"]

    async def get_running_builds(self, sender: MessagePump) -> List[Dict[Any, Any]]:
        """Get a list of running builds

        Args:
            sender (MessagePump): The class that has sent the request.

        Returns:
            List[Dict[Any, Any]]: A lists of build dicts.
        """
        builds = []
        nodes = await self.get_nodes(sender=sender)

        for node in nodes:
            for executor in node["executors"]:
                if not executor["idle"]:
                    executable = executor["currentExecutable"]
                    builds.append(
                        {
                            "name": executable["displayName"],
                            "number": executable["number"],
                            "node": node["displayName"],
                            "progress": executor["progress"],
                            "timestamp": executable["timestamp"],
                        }
                    )

        return builds
