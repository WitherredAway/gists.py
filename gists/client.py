import os
import yarl
import asyncio
import typing
from typing import Optional, Union

import aiohttp

from .constants import API_URL


class GistClient:
    """The client used to interact with the GitHub Gists API.

    Parameters
    ----------
    username: :class:`str`
        The username to be passed to the 'User-Agent' header during requests.
    access_token: :class:`str`
    session: Optional[Union[:class:`aiohttp.ClientSession`]]
    
    Attributes
    ----------
    session: Optional[Union[:class:`aiohttp.ClientSession`]]
        Optional session to be passed to the client during creation.
    """
    def __init__(self, *, username: str, access_token: str, session: Optional[aiohttp.ClientSession] = None):
        self.username = username
        self.access_token = access_token
        self.session = session

        self.URL = 'gists'
        self._request_lock = asyncio.Lock()

    async def _generate_session(self):
        self.session = aiohttp.ClientSession()

    async def request(self, method, *, params=None, data=None, headers=None):
        hdrs = {
            'Accept': "application/vnd.github.inertia-preview+json",
            'User-Agent': self.username,
            'Authorization': "token %s" % self.access_token,
        }

        request_url = yarl.URL(API_URL) / self.URL

        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)

        if not self.session:
            await self._generate_session()

        await self._request_lock.acquire()
        try:
            async with self.session.request(
                    method, request_url, params=params, json=data, headers=hdrs
                ) as response:
                remaining = response.headers.get("X-Ratelimit-Remaining")
                json_data = await response.json()
                if response.status == 429 or remaining == "0":
                    reset_after = float(response.headers.get("X-Ratelimit-Reset-After"))
                    await asyncio.sleep(reset_after)
                    self._request_lock.release()
                    return await self.request(
                        method, url, params=params, data=data, headers=headers
                    )
                elif 300 > response.status >= 200:
                    return json_data
                else:
                    raise response.raise_for_status()
        finally:
            if self._request_lock.locked():
                self._request_lock.release()

    async def fetch_data(self, gist_id: str):
        """Fetch data of a Gist"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        url = "gists/%s" % gist_id

        gist_data_json = await self.request("GET", url, headers=headers)
        return gist_data_json

    async def get_gist(cls, gist_id: str):
        

    @classmethod
    async def create_gist(
        cls,
        access_token: str,
        content: str,
        *,
        description: str = None,
        filename: str = "output.txt",
        public: bool = True,
    ):
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        data = {"public": public, "files": {filename: {"content": content}}}
        params = {"scope": "gist"}

        if description:
            data["description"] = description

        github = Github(access_token)
        js = await github.request(
            "POST", "gists", data=data, headers=headers, params=params
        )
        return await cls.get_gist(access_token, js["id"])

    
class Gist:
    def __init__(self, access_token: str = os.getenv("githubTOKEN")):
        self.access_token = access_token
        self.github = Github(self.access_token)

    @classmethod
    def from_dict(cls, gist_data_dict: typing.Dict):
        

    async def update(self):
        """Re-fetch data and update the instance."""
        updated_gist_data = await self.fetch_data(self.id, self.access_token)
        self.__dict__.update(updated_gist_data)

    async def edit(
        self,
        files: typing.Dict,  # e.g. {"output.txt": {"content": "Content if the file"}}
        *,
        description: str = None,
    ):
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        data = {"files": files}

        if description:
            data["description"] = description

        url = "gists/%s" % self.id

        js = await self.github.request("PATCH", url, data=data, headers=headers)

    async def delete(
        self,
    ):
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        url = "gists/%s" % self.id
        js = await self.github.request("DELETE", url, headers=headers)