from urllib.parse import quote
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
        "link_extension",
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
            link_extension: Sequence[tuple[str, str]] | None = None,
    ):
        self.target = target
        self.rel = rel
        self.title = title
        self.title_star = title_star
        self.anchor = anchor
        self.hreflang = hreflang
        self.type_hint = type_hint
        self.crossorigin = crossorigin
        self.link_extension = link_extension

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

        if self.link_extension is not None:
            header += '; '
            header += '; '.join((f"{k}={v}" for k, v in self.link_extension))

        return header


class Links(list[Link]):

    def as_header(self) -> str:
        return ','.join((link.as_header() for link in self))

    def add(self, *args, **kwargs):
        link = Link(*args, **kwargs)
        self.append(link)
