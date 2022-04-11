import typing
from typing import Optional, Union

import aiohttp

__all__ = (
    "ClientException",
    "HTTPException",
    "AuthorizationFailure",
    "NotFound",
)


class ClientException(Exception):
    """Exception that is raised when an operation in the Client class fails"""

    pass


# Taken from discord.py
def _flatten_error_dict(
    d: typing.Dict[str, typing.Any], key: str = ""
) -> typing.Dict[str, str]:
    items: typing.List[typing.Tuple[str, str]] = []
    for k, v in d.items():
        new_key = key + "." + k if key else k

        if isinstance(v, dict):
            try:
                _errors: typing.List[typing.Dict[str, typing.Any]] = v["_errors"]
            except KeyError:
                items.extend(_flatten_error_dict(v, new_key).items())
            else:
                items.append((new_key, " ".join(x.get("message", "") for x in _errors)))
        else:
            items.append((new_key, v))

    return dict(items)


# Taken from discord.py
class HTTPException(ClientException):
    """Exception that's raised when an HTTP request operation fails.

    Attributes
    ------------
    response: :class:`aiohttp.ClientResponse`
        The response of the failed HTTP request. This is an
        instance of :class:`aiohttp.ClientResponse`. In some cases
        this could also be a :class:`requests.Response`.
    text: :class:`str`
        The text of the error. Could be an empty string.
    status: :class:`int`
        The status code of the HTTP request.
    code: :class:`int`
        The Discord specific error code for the failure.
    """

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        message: Optional[Union[str, typing.Dict[str, typing.Any]]],
    ):
        self.response: aiohttp.ClientResponse = response
        self.status: int = response.status  # type: ignore # This attribute is filled by the library even if using requests
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get("code", 0)
            base = message.get("message", "")
            errors = message.get("errors")
            if errors:
                errors = _flatten_error_dict(errors)
                helpful = "\n".join("In %s: %s" % t for t in errors.items())
                self.text = base + "\n" + helpful
            else:
                self.text = base
        else:
            self.text = message or ""
            self.code = 0

        fmt = "{0.status} {0.reason} (error code: {1})"
        if len(self.text):
            fmt += ": {2}"

        super().__init__(fmt.format(self.response, self.code, self.text))


class AuthorizationFailure(ClientException):
    """Exception that is raised when authorizing provided token in the Client class fails."""

    pass


class NotFound(HTTPException):
    """HTTPException that is raised when the status code is 404"""

    pass
