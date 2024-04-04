class Link:
    __slots__ = ("mimetype", "options")

    target: str
    title: str
    title_star: str
    anchor: str
    hreflang: str
    type_hint: str
    crossorigin: str
    link_extension: str


    quality: float
    formatted: str
    mimetype: MIMEType
    options: Mapping[str, str]


target,
        rel,
        title=None,
        title_star=None,
        anchor=None,
        hreflang=None,
        type_hint=None,
        crossorigin=None,
        link_extension=None,
