import typing
import aiohttp
import sys

from .gist import Gist
from .file import File
from .exceptions import HTTPException, AuthorizationFailure, NotFound, DataFetchError
from .constants import API_URL


__all__ = ("Client",)


class Client:
    """Does not take access token directly to allow actions that do not require authorization.

    Use the authorize method to authorize
    """

    def __init__(self):
        self.access_token = None  # Set by Client.authorize()

    async def authorize(self, access_token: str):
        self.access_token = access_token

        # TODO User object rather than the raw json data
        self.user_data = await self.fetch_user_data()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params=None,
        data=None,
        headers=None,
        authorization: bool = True,
    ) -> typing.Dict:
        """The method to make asynchronous requests to the GitHub API"""

        headers_final = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"Gists.py (https://github.com/witherredaway/gists.py) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}",
        }
        if authorization:
            if not self.access_token:
                raise AuthorizationFailure(
                    "To use functions that require authorization, please authorize the Client with Client.authorize"
                )
            else:
                headers_final["Authorization"] = "token %s" % self.access_token

        request_url = f"{API_URL}/{url}"

        if headers is not None and isinstance(headers, dict):
            headers_final.update(headers)

        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method, request_url, params=params, json=data, headers=headers_final
            )

            try:
                data = await response.json()
            except aiohttp.client_exceptions.ContentTypeError:
                data = response.content
            
            remaining = response.headers.get("X-Ratelimit-Remaining")

            if 300 > response.status >= 200:
                return data
            elif response.status == 429 or remaining == "0":
                raise HTTPException(response, data)
            elif response.status == 404:
                raise NotFound(response, data)
            elif response.status == 401:
                raise AuthorizationFailure(
                    "Invalid personal access token has been passed."
                )

    async def fetch_user_data(self) -> typing.Dict:
        """Fetch data of the authenticated user"""

        try:
            # TODO User object rather than the raw json data
            user_data: typing.Dict = await self.request(
                "GET", "user", authorization=True
            )
        except NotFound as error:
            raise NotFound(error.response, "User not found")

        return user_data

    async def fetch_gist_data(self, gist_id: str) -> typing.Dict:
        """Fetch data of a Gist"""

        try:
            gist_data: typing.Dict = await self.request(
                "GET", "gists/%s" % gist_id, authorization=False
            )
        except NotFound as error:
            raise NotFound(error.response, "Gist not found")
        return gist_data

    async def get_gist(self, gist_id: str) -> Gist:
        """Get a Gist object representing the gist associated with the provided gist_id

        Does not require authorization.
        """

        data = await self.fetch_gist_data(gist_id)
        return Gist(data, self)

    async def create_gist(
        self,
        *,
        files: typing.List[File],
        description: str = None,
        public: bool = True,
    ) -> Gist:
        """Create a new gist and return a Gist object associated with that gist"""

        files_dict = {}
        for file in files:
            # Update the files_dict with the dictionaries of each File object
            files_dict.update(file.to_dict())

        data = {"public": public, "files": files_dict}
        params = {"scope": "gist"}

        if description:
            data["description"] = description

        js = await self.request("POST", "gists", data=data, params=params)
        return Gist(js, self)

    async def update_gist(self, gist_id: str):
        """Alias of fetch_gist_data, used to fetch a gist's data."""

        updated_gist_data = await self.fetch_gist_data(gist_id)
        return updated_gist_data

    async def edit_gist(
        self,
        gist_id: str,
        *,
        files: typing.List[File],
        description: str = None,
    ) -> typing.Dict:
        """Edit the gist associated with the provided gist id, and return the edited data"""

        files_dict = {}
        for file in files:
            # Update the files_dict with the dictionaries of each File object
            files_dict.update(file.to_dict())

        data = {"files": files_dict}

        if description:
            data["description"] = description

        try:
            edited_gist_data = await self.request(
                "PATCH", "gists/%s" % gist_id, data=data
            )
        except NotFound as error:
            raise NotFound(error.response, "Gist not found")
        return edited_gist_data

    async def delete_gist(self, gist_id: str):
        """Delete the gist associated with the provided gist id"""

        try:
            await self.request("DELETE", "gists/%s" % gist_id)
        except NotFound as error:
            raise NotFound(error.response, "Gist not found")
