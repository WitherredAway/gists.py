import typing
from typing import Optional, TypeVar, Type
from types import TracebackType
import yarl
import asyncio
import aiohttp
import sys

from .gist import Gist
from .exceptions import ClientAuthorizationError
from .constants import API_URL


__all__ = ("Client",)


class Client:
    def __init__(self, access_token: str):
        self.access_token = access_token

        self._request_lock = asyncio.Lock()
        self.user_agent = f"Gists.py (https://github.com/witherredaway/gists.py) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}"

    async def request(
        self, method: str, url: str, *, params=None, data=None, headers=None
    ) -> typing.Dict:
        """The method to make asynchronous requests to the GitHub API"""

        hdrs = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": self.user_agent,
            "Authorization": "token %s" % self.access_token,
        }

        request_url = yarl.URL(API_URL) / url

        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)

        await self._request_lock.acquire()
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method, request_url, params=params, json=data, headers=hdrs
                )
                remaining = response.headers.get("X-Ratelimit-Remaining")
                try:
                    data = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    data = response.content
                if response.status == 429 or remaining == "0":
                    reset_after = float(response.headers.get("X-Ratelimit-Reset-After"))
                    await asyncio.sleep(reset_after)
                    self._request_lock.release()
                    return await self.request(
                        method, request_url, params=params, data=data, headers=headers
                    )
                elif 300 > response.status >= 200:
                    return data
                else:
                    raise response.raise_for_status()
        finally:
            if self._request_lock.locked():
                self._request_lock.release()

    async def get_user_data(self) -> typing.Dict:
        user_data = await self.fetch_user()
        return user_data

    async def fetch_user(self) -> typing.Dict:
        """Fetch data of the authenticated user"""

        user_data: typing.Dict = await self.request("GET", "user")
        return user_data

    async def fetch_data(self, gist_id: str) -> typing.Dict:
        """Fetch data of a Gist"""

        gist_data: typing.Dict = await self.request("GET", "gists/%s" % gist_id)
        return gist_data

    async def get_gist(self, gist_id: str) -> Gist:
        """Get a Gist object representing the gist associated with the provided gist_id"""

        data = await self.fetch_data(gist_id)
        return Gist(data, self)

    async def create_gist(
        self,
        files: typing.Dict,  # e.g. {"output.txt": {"content": "Content of the file"}}
        *,
        description: str = None,
        public: bool = True,
    ) -> Gist:
        """Create a new gist and return a Gist object associated with that gist"""

        data = {"public": public, "files": files}
        params = {"scope": "gist"}

        if description:
            data["description"] = description

        js = await self.request("POST", "gists", data=data, params=params)
        return Gist(js, self)

    async def update_gist(self, gist_id: str):
        """Re-fetch data and update the provided Gist object."""

        updated_gist_data = await self.fetch_data(gist_id)
        return updated_gist_data

    async def edit_gist(
        self,
        gist_id: str,
        *,
        files: typing.Dict,  # e.g. {"output.txt": {"content": "Content of the file"}}
        description: str = None,
    ) -> typing.Dict:
        """Edit the gist associated with the provided gist id, and return the edited data"""

        data = {"files": files}

        if description:
            data["description"] = description

        edited_gist_data = await self.request("PATCH", "gists/%s" % gist_id, data=data)
        return edited_gist_data

    async def delete_gist(self, gist_id: str):
        """Delete the gist associated with the provided gist id"""

        await self.request("DELETE", "gists/%s" % gist_id)
