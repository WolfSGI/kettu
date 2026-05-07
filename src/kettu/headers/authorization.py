import re
from typing import NamedTuple, ClassVar


auth_params_reg = re.compile(
    r'([a-z]+)[ \t]*=[ \t]*(".*?"|[^,]*?)[ \t]*(?:\Z|, *)')


class DigestAuthParams(NamedTuple):
    realm: str | None = None
    username: str | None = None
    uri: str | None = None
    algorithm: str | None = None
    nonce: str | None = None
    nc: str | None = None
    cnonce: str | None = None
    qop: str | None = None
    response: str | None = None
    opaque: str | None = None
    userhash: str = "false"

    @classmethod
    def from_string(cls, value: str):
        params = {
            k: v.strip().strip('"')
            for k, v in auth_params_reg.findall(value)
        }
        return cls(**params)


class Authorization(NamedTuple):
    scheme: str
    credentials: str | DigestAuthParams

    @classmethod
    def from_string(cls, value: str):
        scheme, _, credentials = value.strip(' ').partition(' ')
        scheme = scheme.lower()
        if scheme == "digest":
            return cls(scheme, DigestAuthParams.from_string(credentials))
        return cls(scheme, credentials.strip())
