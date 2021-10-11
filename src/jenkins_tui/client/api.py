import socket
import httpx

from typing import Any, Dict, List, Optional
from httpx._auth import BasicAuth


class Jenkins:
    "A basic Jenkins HTTP client with async support"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        timeout: Optional[float] = None,
    ) -> None:
        """Create a Jenkins instance.

        Args:
            url (str): The url of the Jenkins server.
            username (str): [description]. The username of the user permitted to access the Jenkins server.
            password (str): [description]. The password of the user permitted to access the Jenkins server.
            timeout (int, optional): The request timeout. Defaults to socket._GLOBAL_DEFAULT_TIMEOUT.
        """

        if url.endswith("/"):
            url = url.strip("/")

        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout if timeout else socket.getdefaulttimeout()

        self.auth = BasicAuth(username.encode("utf-8"), password.encode("utf-8"))

    def _request(self, endpoint: str, method: str = "GET") -> httpx.Response:
        """Send a http request via the Jenkins client.

        Args:
            endpoint (str): The api endpoint.
            method (str, optional): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            httpx.Response: A requests.Response instance.
        """

        full_url = f"{self.url}/{endpoint}"

        with httpx.Client(timeout=self.timeout, auth=self.auth) as client:
            response = client.request(method=method, url=full_url)
            response.raise_for_status()
            return response

    async def _request_async(
        self, endpoint: str, method: str = "GET"
    ) -> httpx.Response:
        """Send a http request via the Jenkins client.

        Args:
            endpoint (str): The api endpoint.
            method (str, optional): A Valid HTTP method. Defaults to 'GET'.

        Returns:
            requests.Response: A requests.Response instance.
        """

        full_url = f"{self.url}/{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout, auth=self.auth) as client:
            response = await client.request(method=method, url=full_url, auth=self.auth)
            response.raise_for_status()
            return response

    def test_connection(self) -> bool:
        """Test the connection to the Jenkins server.

        Returns:
            bool: True if the connection is valid.
        """
        _ = self._request(endpoint=f"api/json")
        return True

    async def get_nodes(self) -> List[Dict[Any, Any]]:
        """Get a list of nodes from the server

        Returns:
            List[Dict[Any, Any]]: A list of node dicts.
        """
        endpoint = (
            "computer/api/json?tree=*,computer[*,executors[*,currentExecutable[*]]]"
        )
        response = await self._request_async(endpoint=endpoint)
        return response.json()["computer"]

    async def get_job(self, path: str = None, limit: int = 20) -> List[Dict[Any, Any]]:
        """Get a job and it's details.

        Args:
            path (str, optional): The path to the job.
            limit (int, optional): The maximum number of builds that will be returned with the job. Defaults to 20.

        Returns:
            List[Dict[Any, Any]]: [description]
        """
        _limit = f"{{0,{limit}}}"
        endpoint = f"{path}api/json?tree=displayName,description,healthReport[description],builds[number,status,timestamp,id,result,duration{_limit}]"
        response = await self._request_async(endpoint=endpoint)
        return response.json()

    async def get_jobs(
        self, path: str = None, recursive=False, folder_depth=10
    ) -> List[Dict[Any, Any]]:
        """Return a list of jobs starting from the root of the server.

        Args:
            path (str, optional): The path to node that has nested jobs. Defaults to None.
            recursive (bool, optional): If true the method will recursively build the query up to folder_depth. Defaults to False.
            folder_depth (int, optional): The maximum level of recursion while gathering nested jobs. Has no impact if recursive is False. Defaults to 10.

        Returns:
            List[Dict[Any, Any]]: [description]
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

    async def get_info_for_job(self, path: str) -> Dict[Any, Any]:
        """Get top level information about a job. The query used in this method will
        return: displayName,description and healthReport

        Args:
            path (str): The path to the job. If the job is nested in a folder it could be /job/{folder}/{job}/my-job.

        Returns:
            Dict[Any, Any]: A dict containing information about the job.
        """
        endpoint = (
            f"{path}api/json?tree=displayName,description,healthReport[description]"
        )
        response = await self._request_async(endpoint=endpoint)
        return response.json()

    async def get_builds_for_job(
        self, path: str, limit: int = 20
    ) -> List[Dict[Any, Any]]:
        """Get a list of builds for a job.

        Args:
            path (str): The path to the job. If the job is nested in a folder it could be /job/{folder}/{job}/my-job.
            limit (int): The maximum number of jobs to return. Defaults to 20.

        Returns:
            List[Dict[Any, Any]]: A list of builds.
        """
        _limit = f"{{0,{limit}}}"
        endpoint = f"{path}api/json?tree=builds[number,status,timestamp,id,result,duration{_limit}]"
        response = await self._request_async(endpoint=endpoint)
        return response.json()["builds"]

    async def get_running_builds(self) -> List[Dict[Any, Any]]:
        """Get a list of running builds on the server.

        Returns:
            List[Dict[Any, Any]]: A lists of build dicts.
        """
        builds = []
        nodes = await self.get_nodes()

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

    async def get_queued_jobs(self) -> List[Dict[Any, Any]]:
        """Get queued jobs.

        Returns:
            List[Dict[Any, Any]]: A list of jobs that are currently queued.
        """
        endpoint = "/queue/api/json?tree=items[id,inQueueSince,why]"
        response = await self._request_async(endpoint=endpoint)
        return response.json()["items"]