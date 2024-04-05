import orjson
from pathlib import Path
from typing import Generic, TypeVar, AnyStr, Any
from collections.abc import Mapping, Iterable, Iterator, Callable, MutableMapping, Sequence
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


class Headers(MutableMapping[str, str]):
    __slots__ = ("_cookies", "_links", "_headers")

    _cookies: Cookies | None
    _links: Links | None
    _headers: MutableMapping

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

    def __new__(
            cls,
            data: MutableMapping[str, str] | \
                Sequence[tuple[str, str]] | None = None
    ):
        if data is not None and isinstance(data, cls):
            return data
        inst = super().__new__(cls)
        inst._cookies = None
        inst._links = None
        inst._headers = {}
        if data:
            if isinstance(data, dict):
                for key, value in data.items():
                    inst[key] = value
            elif isinstance(data, (list, tuple)):
                for key, value in data:
                    inst.add(key, value)
        return inst

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

    def __repr__(self):
        return f"<{self.__class__.__name__}: [{len(self)}]>"

    def __getitem__(self, name: str):
        return self._headers[name.title()]

    def __len__(self):
        length = len(self._headers)
        if self._cookies:
            length += 1
        if self._links:
            length += 1
        return length

    def __contains__(self, name: str):
        name = name.title()
        if name == "Link":
            return bool(self._links)
        if name == "Set-Cookie":
            return bool(self._cookies)
        return name in self._headers

    def __bool__(self):
        return (
            bool(self._headers) or
            bool(self._cookies) or
            bool(self._links)
        )

    def __setitem__(self, name: str, value: str):
        name = name.title()
        if name in ('Set-Cookie', 'Link'):
            raise KeyError()
        self._headers[name] = value

    def __delitem__(self, name: str):
        name = name.title()
        if name == "Set-Cookie":
            self._cookies = None
        elif name == "Link":
            self._links = None
        else:
            del self._headers[name]

    def add(self, name: str, value: str, merge: bool = True):
        if name in self and merge:
            self[name] += ", " + value
        else:
            self[name] = value

    def __iter__(self):
        yield from self._headers.keys()
        if self._cookies:
            yield "Set-Cookie"
        if self._links:
            yield "Link"

    def items(self):
        yield from self._headers.items()
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
