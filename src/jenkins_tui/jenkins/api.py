from __future__ import annotations

import socket
from typing import Any
from urllib.parse import urlencode

import httpx
from httpx._auth import BasicAuth


class Jenkins:
    "A basic Jenkins HTTP client with async support"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        timeout: float | None = None,
    ) -> None:
        """Create a Jenkins instance.

        Args:
            url (str): The url of the Jenkins server.
            username (str): [description]. The username of the user permitted to access the Jenkins server.
            password (str): [description]. The password of the user permitted to access the Jenkins server.
            timeout (float | None): The request timeout. Defaults to socket._GLOBAL_DEFAULT_TIMEOUT.
        """
        self.url = url.strip("/") if url.endswith("/") else url
        self.timeout = timeout if timeout else socket.getdefaulttimeout()
        self.auth = BasicAuth(username.encode("utf-8"), password.encode("utf-8"))
        self.version = ""
        self.description = ""

        self.test_connection()

    def test_connection(self) -> None:
        """Test the connection to the Jenkins server."""

        with httpx.Client(
            timeout=self.timeout, auth=self.auth, base_url=self.url
        ) as client:
            response = client.request(method="GET", url="/api/json")
            response.raise_for_status()

            self.version = response.headers["X-Jenkins"]
            self.description = response.json().get("description", "")

    async def _request_async(
        self, endpoint: str, method: str = "GET"
    ) -> httpx.Response:
        """Send a http request via the Jenkins client.

        Args:
            endpoint (str): The api endpoint.
            method (str): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            requests.Response: A requests.Response instance.
        """
        async with httpx.AsyncClient(
            timeout=self.timeout, auth=self.auth, base_url=self.url
        ) as client:

            headers = {}

            if method != "GET":
                crumb_issuer_enderpoint = "crumbIssuer/api/json"
                crumb_response = await client.request(
                    method="GET", url=crumb_issuer_enderpoint
                )
                headers["Jenkins-Crumb"] = crumb_response.json()["crumb"]

            response = await client.request(
                method=method, url=endpoint, headers=headers
            )

            response.raise_for_status()
            return response

    async def get_nodes(self) -> list[dict[Any, Any]]:
        """Get a list of nodes from the server

        Returns:
            list[dict[Any, Any]]: A list of node dicts.
        """
        endpoint = (
            "computer/api/json?tree=*,computer[*,executors[*,currentExecutable[*]]]"
        )
        response = await self._request_async(endpoint=endpoint)
        return response.json()["computer"]

    async def get_job(self, path: str | None = None, limit: int = 20) -> dict[Any, Any]:
        """Get a job and it's details.

        Args:
            path (str | None): The path to the job.
            limit (int): The maximum number of builds that will be returned with the job. Defaults to 20.

        Returns:
            list[dict[Any, Any]]: [description]
        """
        _limit = f"{{0,{limit}}}"
        endpoint = f"{path}api/json?tree=name,displayName,description,actions[parameterDefinitions[*]],property[parameterDefinitions[*,defaultParameterValue[*]]],healthReport[description],builds[number,status,description,timestamp,id,result,duration,changeSets[*[*]]{_limit}]"
        response = await self._request_async(endpoint=endpoint)
        return response.json()

    async def get_jobs(
        self,
        path: str = None,
        recursive: bool = False,
        folder_depth: int = 10,
    ) -> list[dict[Any, Any]]:
        """Return a list of jobs starting from the root of the server.

        Args:
            path (str): The path to node that has nested jobs. Defaults to None.
            recursive (bool): If true the method will recursively build the query up to folder_depth. Defaults to False.
            folder_depth (int): The maximum level of recursion while gathering nested jobs. Has no impact if recursive is False. Defaults to 10.

        Returns:
            list[dict[Any, Any]]: [description]
        """
        if recursive:
            jobs_query = "jobs"
            for _ in range(folder_depth):
                jobs_query = f"jobs[url,color,name,{jobs_query}]"
            base = f"api/json?tree={jobs_query}"
        else:
            base = "api/json?tree=jobs[url,color,name]"
        endpoint = f"{path}/{base}" if path else f"/{base}"

        response = await self._request_async(endpoint=endpoint)
        return response.json()["jobs"]

    async def get_running_builds(self) -> list[dict[Any, Any]]:
        """Get a list of running builds on the server.

        Returns:
            list[dict[Any, Any]]: A lists of build dicts.
        """
        builds = []
        nodes = await self.get_nodes()

        for node in nodes:
            for executor in node["executors"]:
                if not executor["idle"]:
                    executable = executor["currentExecutable"]

                    builds.append(
                        {
                            "name": executable["fullDisplayName"],
                            "number": executable["number"],
                            "node": node["displayName"],
                            "progress": executor["progress"],
                            "timestamp": executable["timestamp"],
                        }
                    )

        return builds

    async def get_queued_jobs(self) -> list[dict[Any, Any]]:
        """Get queued jobs.

        Returns:
            list[dict[Any, Any]]: A list of jobs that are currently queued.
        """

        endpoint = "/queue/api/json?tree=items[*,task[*]]"
        response = await self._request_async(endpoint=endpoint)
        return response.json()["items"]

    async def build(self, path: str, parameters: dict[str, str] | None = None) -> int:
        """Build a job.

        Args:
            path (str): The path to the job. If the job is nested in a folder it could be /job/{folder}/{job}/my-job.
            parameters (dict[str, str] | None): A dict of parameters to pass to the job.

        Returns:
            int: A requests.Response instance.
        """

        if not parameters:
            endpoint = f"{path}build"
        else:
            endpoint = f"{path}buildWithParameters?{urlencode(parameters)}"

        response = await self._request_async(endpoint=endpoint, method="POST")

        location = response.headers["Location"]
        if location.endswith("/"):
            location = location[:-1]

        queue_id = location.split("/")[-1]

        return int(queue_id)
