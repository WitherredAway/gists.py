import typing
import datetime

from .file import File
from .constants import TIME_FORMAT


__all__ = ("Gist",)


class Gist:
    """The Gist object that represents a gist"""

    __slots__ = (
        "client",
        "comments",
        "comments_url",
        "commits_url",
        "_created_at",
        "description",
        "_files",
        "forks",
        "forks_url",
        "git_pull_url",
        "git_push_url",
        "history",
        "url",
        "id",
        "node_id",
        "owner",
        "public",
        "truncated",
        "_updated_at",
        "api_url",
        "user",
    )

    def __init__(self, data: typing.Dict, client: "Client"):
        self.client = client

        self._update_attrs(data)

    def _update_attrs(self, data: typing.Dict):
        """Update the Gist object's attributes with the provided data"""

        self.comments: int = data.get("comments", None)
        self.comments_url: str = data.get("comments_url", None)
        self.commits_url: str = data.get("commits_url", None)
        self._created_at: str = data.get("created_at", None)
        self.description: str = data.get("description", None)
        self._files: typing.Dict = data.get("files", None)
        self.forks: typing.List = data.get("forks", None)  # TODO Fork object
        self.forks_url: str = data.get("forks_url", None)
        self.git_pull_url: str = data.get("git_pull_url", None)
        self.git_push_url: str = data.get("git_push_url", None)
        self.history: typing.List = data.get("history", None)  # TODO History object
        self.url: str = data.get("html_url", None)
        self.id: str = data.get("id", None)
        self.node_id: str = data.get("node_id", None)
        self.owner: typing.Dict = data.get("owner", None)  # TODO User object
        self.public: bool = data.get("public", None)
        self.truncated: bool = data.get("truncated", None)
        self._updated_at: str = data.get("updated_at", None)
        self.api_url: str = data.get("url", None)
        self.user: None = data.get("user", None)

    def _get_dt_obj(self, time: str) -> datetime.datetime:
        time = time + " +0000"  # Tells datetime that the timezone is UTC
        dt_obj: datetime.datetime = datetime.datetime.strptime(time, TIME_FORMAT)
        return dt_obj

    @property
    def created_at(self) -> datetime.datetime:
        return self._get_dt_obj(self._created_at)

    @created_at.setter
    def created_at(self, value: str):
        self._created_at = value

    @property
    def files(self) -> typing.List[File]:
        file_objs: typing.List[File] = File.from_dict(self._files)
        return file_objs

    @files.setter
    def files(self, value: typing.Dict):
        self._files = value

    @property
    def updated_at(self) -> datetime.datetime:
        return self._get_dt_obj(self._updated_at)

    @updated_at.setter
    def updated_at(self, value: str):
        self._updated_at = value

    async def update(self):
        """Fetch and update the Gist object with the gist"""

        updated_gist_data = await self.client.update_gist(self.id)
        self._update_attrs(updated_gist_data)

    async def edit(self, *, files: typing.List[File], description: str = None):
        """Edit the gist associated with the Gist object, then update the Gist object"""

        edited_gist_data = await self.client.edit_gist(
            self.id, files=files, description=description
        )
        self._update_attrs(edited_gist_data)

    async def delete(self):
        """Delete the gist associated with the Gist object, then delete the Gist object itself"""

        await self.client.delete_gist(self.id)
