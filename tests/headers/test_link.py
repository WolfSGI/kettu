from kettu.headers.link import Link, Links


def test_simple_link():
    link = Link("http://example.com/TheBook/chapter2", "previous")
    assert link.as_header() == (
        "<http://example.com/TheBook/chapter2>; rel=previous"
    )
    parsed_link = link.from_string(link.as_header())
    assert link == parsed_link

    link = Link("/", "http://example.net/foo")
    assert link.as_header() == '</>; rel="http://example.net/foo"'
    parsed_link = link.from_string(link.as_header())
    assert link == parsed_link

    link = Link("/terms", "copyright", anchor="#foo")
    assert link.as_header() == '</terms>; rel=copyright; anchor="#foo"'
    parsed_link = link.from_string(link.as_header())
    assert link == parsed_link


def test_links():
    value = (
        "<http://example.com/TheBook/chapter2>; rel=previous,"
        '</terms>; rel=copyright; anchor="#foo"'
    )
    links = Links.from_string(value)
    assert len(links) == 2
    assert links == [
        Link("http://example.com/TheBook/chapter2", "previous"),
        Link("/terms", "copyright", anchor="#foo")
    ]
