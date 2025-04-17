import re
from urllib.request import parse_http_list
from urllib.parse import quote, urlsplit, urlunsplit
from pathlib import PurePosixPath
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


# Borrowed from Sanic
# CGI parse header is deprecated.
_token, _quoted = r"([\w!#$%&'*+\-.^_`|~]+)", r'"([^"]*)"'
_param = re.compile(rf";\s*{_token}=(?:{_token}|{_quoted})", re.ASCII)


# Safe characters
_safe_uri_path_chars = "+&=/"
_safe_uri_query_chars = "?/="
_safe_uri_fragment_chars = "?/#+&="


def dequote(value: str) -> str:
    """If a value has double quotes around it, remove them.
    """
    if (len(value) >= 2 and value[0] == value[-1]) and value.startswith('"'):
        return value[1:-1]
    return value


def encode_uri(value: str):
    (scheme, netloc, path, query, fragment) = urlsplit(value)
    if path:
        path = quote(path, safe=_safe_uri_path_chars)
    if query:
        query = quote(query, safe=_safe_uri_query_chars)
    if fragment:
        fragment = quote(fragment, safe=_safe_uri_fragment_chars)
    return urlunsplit((scheme, netloc, path, query, fragment))


def parse_list_header(value: str) -> tuple[str]:
    return tuple((dequote(header) for header in parse_http_list(value)))


def parse_header(value: str) -> tuple[str, dict[str, str]]:
    pos = value.find(";")
    if pos == -1:
        options = {}
    else:
        options = {
            m.group(1).lower(): (m.group(2) or m.group(3))
            .replace("%22", '"')
            .replace("%0D%0A", "\n")
            for m in _param.finditer(value[pos:])
        }
        value = value[:pos]
    return value.strip().lower(), options


parse_http_datetime = parsedate_to_datetime


def serialize_http_datetime(dt: datetime) -> str:
    """Returns an RFC 1123 datetime string
    """
    if dt.tzinfo is None:
        # If the datetime is naive, we assume its utc.
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def parse_host(value: str) -> tuple[str | None, int | None]:
    # RFC 3986 § 3.2.2
    # IP-literal containing an IPv6 (or later) address
    if value.startswith('['):
        # In cast of an IP-Literal, we keep the brackets.
        pos = value.rfind(']:')
        # Does it contain a port ?
        if pos != -1:
            return value[:pos + 1], int(value[pos + 2:])
        return value, None

    # Basic domain or IPv4, with or without port
    name, _, port = value.partition(':')
    if not port:
        return value, None
    return name, int(port)


def parse_wsgi_path(path: str) -> str:
    # according to PEP 3333 the native string representing PATH_INFO
    # (and others) can only contain unicode codepoints from 0 to 255,
    # which is why we need to decode to latin-1 instead of utf-8 here.
    # We transform it back to UTF-8
    # Note that it's valid for WSGI server to omit the value if it's
    # empty.
    if path:
        return str(PurePosixPath(path.encode("latin-1").decode("utf-8")))
    return "/"
