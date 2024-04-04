import orjson
from pathlib import Path
from typing import Generic, TypeVar, AnyStr, Any
from collections import UserDict
from collections.abc import Mapping, Iterable, Iterator, Callable
from http import HTTPStatus
from collections import deque
from kettu.http.headers import Cookies, ContentType, ETag, Links
from kettu.http.headers.utils import serialize_http_datetime
from kettu.http.constants import EMPTY_STATUSES, REDIRECT_STATUSES
from kettu.http.types import HTTPCode


BodyT = str | bytes | Iterator[bytes]
HeadersT = Mapping[str, str] | Iterable[tuple[str, str]]
F = TypeVar("F", bound=Callable)


UNSET = object()


def header_property(
        name: str,
        *,
        caster=None,
        documentation="",
):

    name = name.title()

    def getter(self):
        try:
            return self[name]
        except KeyError:
            return UNSET

    def setter(self, value):
        if value is None:
            del self[name]
            return
        if caster is not None:
            value = caster(value)
        self[name] = value

    def remover(self):
        del self[name]

    return property(getter, setter, remover, documentation)


class Headers(UserDict[str, str]):
    __slots__ = ("_cookies", "_links")

    _cookies: Cookies | None
    _links: Links | None

    last_modified = header_property(
        'Last-Modified', caster=serialize_http_datetime
    )

    accept_ranges = header_property(
        'Accept-Ranges'
    )

    content_type = header_property(
        'Content-Type', caster=ContentType.caster
    )

    etag = header_property(
        'ETag', caster=ETag.caster
    )

    expires = header_property(
        'Expires', caster=serialize_http_datetime
    )

    def __new__(cls, *args, **kwargs):
        if not kwargs and len(args) == 1 and isinstance(args[0], cls):
            return args[0]
        inst = super().__new__(cls)
        inst._cookies = None
        inst._links = None
        return inst

    def __init__(self, value=None):
        if value:
            if isinstance(value, dict):
                super().__init__(value)
            elif isinstance(value, (list, tuple)):
                super().__init__()
                for key, value in value:
                    self.add(key, value)
        else:
            super().__init__()

    @property
    def cookies(self) -> Cookies:
        if self._cookies is None:
            self._cookies = Cookies()
        return self._cookies

    @property
    def links(self) -> Links:
        if self._links is None:
            self._links = Links()
        return self._links

    def __getitem__(self, name: str):
        name = name.title()
        return super().__getitem__(name)

    def __len__(self):
        length = len(self.data)
        if self._cookies:
            length += 1
        if self._links:
            length += 1
        return length

    def __contains__(self, name: str):
        name = name.title()
        return super().__contains__(name)

    def __bool__(self):
        return bool(self.data) or self._cookies or self._links

    def __setitem__(self, name: str, value: str):
        self.add(name, value, merge=False)

    def add(self, name: str, value: str, merge: bool = True):
        name = name.title()

        if name in ('Set-Cookie', 'Link'):
            raise KeyError()

        if name in self and merge:
            value = self[name] + ", " + value
            super().__setitem__(name, value)
        else:
            super().__setitem__(name, value)

    def items(self):
        yield from super().items()
        if self._cookies:
            yield "Set-Cookie", self._cookies.as_header()
        if self._links:
            yield "Link", self._links.as_header()


class FileResponse:

    __slots__ = ("status", "block_size", "headers", "filepath")

    def __init__(
        self,
        filepath: Path,
        status: HTTPCode = 200,
        block_size: int = 4096,
        headers: HeadersT | None = None,
    ):
        self.status = HTTPStatus(status)
        self.filepath = filepath
        self.headers = Headers(headers or ())  # idempotent.
        self.block_size = block_size


class Response(Generic[F]):
    __slots__ = ("status", "body", "headers", "_finishers")

    status: HTTPStatus
    headers: Headers
    body: BodyT | None
    _finishers: deque[F] | None

    def __init__(
        self,
        status: HTTPCode = 200,
        body: BodyT | None = None,
        headers: HeadersT | None = None,
    ):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = Headers(headers or ())  # idempotent.
        self._finishers = None

    def add_finisher(self, task: F):
        if self._finishers is None:
            self._finishers = deque([task])
        else:
            self._finishers.append(task)

    @property
    def cookies(self) -> Cookies:
        return self.headers.cookies

    def __iter__(self) -> Iterator[bytes]:
        if self.status not in EMPTY_STATUSES:
            if self.body is None:
                yield self.status.description.encode()
            elif isinstance(self.body, bytes):
                yield self.body
            elif isinstance(self.body, str):
                yield self.body.encode()
            elif isinstance(self.body, Iterator):
                yield from self.body
            else:
                raise TypeError(
                    f"Body of type {type(self.body)!r} is not supported.")

    @classmethod
    def to_json(
        cls,
        code: HTTPCode = 200,
        body: BodyT | None = None,
        headers: HeadersT | None = None,
    ) -> "Response":
        data = orjson.dumps(body)
        if headers is None:
            headers = {"Content-Type": "application/json"}
        else:
            headers = Headers(headers)
            headers["Content-Type"] = "application/json"
        return cls(code, data, headers)

    @classmethod
    def html(
        cls,
        code: HTTPCode = 200,
            body: AnyStr = b"",
            headers: HeadersT | None = None,
    ) -> "Response":
        if headers is None:
            headers = {"Content-Type": "text/html; charset=utf-8"}
        else:
            headers = Headers(headers)
            headers["Content-Type"] = "text/html; charset=utf-8"
        return cls(code, body, headers)

    @classmethod
    def redirect(
        cls,
        location,
        code: HTTPCode = 303,
        body: BodyT | None = None,
        headers: HeadersT | None = None,
    ) -> "Response":
        if code not in REDIRECT_STATUSES:
            raise ValueError(f"{code}: unknown redirection code.")
        if not headers:
            headers = {"Location": location}
        else:
            headers = Headers(headers)
            headers["Location"] = location
        return cls(code, body, headers)
