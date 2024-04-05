from urllib.parse import quote
from typing import NamedTuple
from collections.abc import Sequence


class Link:

    __slots__ = (
        "target",
        "rel",
        "title",
        "title_star",
        "anchor",
        "hreflang",
        "type_hint",
        "crossorigin",
        "extensions",
    )

    def __init__(
            self,
            target: str,
            rel: str,
            title: str | None = None,
            title_star: tuple[str, str] | None = None,
            anchor: str | None = None,
            hreflang: str | Sequence[str] | None = None,
            type_hint: str | None = None,
            crossorigin: str | None = None,
            **extensions: str
    ):
        self.target = target
        self.rel = rel
        self.title = title
        self.title_star = title_star
        self.anchor = anchor
        self.hreflang = hreflang
        self.type_hint = type_hint
        self.crossorigin = crossorigin
        self.extensions = extensions or None

    def __eq__(self, other: 'Link'):
        return (
            self.target==other.target,
            self.rel==other.rel,
            self.title==other.title,
            self.title_star==other.title_star,
            self.anchor==other.anchor,
            self.hreflang==other.hreflang,
            self.type_hint==other.type_hint,
            self.crossorigin==other.crossorigin,
            self.extensions==other.extensions
        )

    def __hash__(self):
        return (
            hash(self.target),
            hash(self.rel),
            hash(self.title),
            hash(self.title_star),
            hash(self.anchor),
            hash(self.hreflang),
            hash(self.type_hint),
            hash(self.crossorigin),
            hash(self.extensions)
        )

    @classmethod
    def from_string(cls, value):
        replace_chars = " '\""
        # This will raise a ValueError if there no 'rel'
        url, params = value.split(";", 1)
        args = {}
        for param in params.split(";"):
            key, value = param.split("=")
            if key == 'title*':
                key = "title_star"
            args[key.strip(replace_chars)] = value.strip(replace_chars)

        return cls(
            url.strip("<> '\""),
            args.pop('rel'),
            **args
        )

    def as_header(self):
        header = '<' + quote(self.target, safe=':/') + '>'
        if '//' in self.rel:
            header += '; rel="' + quote(self.rel, safe=' :/') + '"'
        else:
            header += '; rel=' + self.rel

        if self.title is not None:
            header += '; title="' + self.title + '"'

        if self.title_star is not None:
            header += (
                "; title*=UTF-8'"
                + self.title_star[0]
                + "'"
                + quote(self.title_star[1])
            )

        if self.type_hint is not None:
            header += '; type="' + self.type_hint + '"'

        if self.hreflang is not None:
            if isinstance(self.hreflang, str):
                header += '; hreflang=' + self.hreflang
            else:
                header += '; '
                header += '; '.join(
                    ('hreflang=' + lang for lang in self.hreflang)
                )

        if self.anchor is not None:
            header += '; anchor="' + quote(self.anchor, safe="#") + '"'

        if self.crossorigin is not None:
            crossorigin = self.crossorigin.lower()
            if crossorigin == 'anonymous':
                header += '; crossorigin'
            elif crossorigin == 'use-credentials':
                header += '; crossorigin="use-credentials"'
            else:
                raise ValueError()

        if self.extensions is not None:
            header += '; '
            header += '; '.join((f"{k}={v}" for k, v in self.extensions))

        return header


class Links(list[Link]):

    def as_header(self) -> str:
        return ','.join((link.as_header() for link in self))

    @classmethod
    def from_string(cls, value):
        return cls((
            Link.from_string(linkstr)
            for linkstr in value.split(',')
        ))

    def add(self, *args, **kwargs):
        link = Link(*args, **kwargs)
        self.append(link)
