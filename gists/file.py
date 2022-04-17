import typing
from typing import Optional, TypeVar


__all__ = ("File",)

F = TypeVar("F", bound="File")


class File:
    """The file object that is provided when editing and creating gists"""

    def __init__(self, *, name: str, content: Optional[str] = None, new_name: Optional[str] = None):
        self.name: str = name
        self.content: str = content

        self.new_name: str = new_name or self.name

    def to_dict(self) -> typing.Dict:
        """Returns the dictionary form of the File object"""

        files_dict = {
            self.name: {
                "filename": self.new_name
            }
        }

        if self.content:
            content_dict = {"content": self.content}
            files_dict[self.name].update(content_dict)
            
        return files_dict

    @classmethod
    def from_dict(cls, files_dict: typing.Dict) -> typing.List[F]:
        """Returns a list of File objects from a files dictionary"""

        # Example structure of a files_dict:
        #     {
        # "file1.txt": {
        #   "content": ""
        # },
        # "file2.txt": {
        #   "filename": "file2.txt",
        #   "content": "test"
        # },
        # }

        file_objs = []
        for name, value in files_dict.items():
            self = cls.__new__(cls)

            self.name = name
            self.content = files_dict[name].get("content", None)
            self.new_name = files_dict[name].get("filename", self.name)

            file_objs.append(self)

        return file_objs
