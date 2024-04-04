from kettu.http.headers.link import Link


def test_simple_link():
    link = Link("http://example.com/TheBook/chapter2", "previous")
    assert link.as_header() == "<http://example.com/TheBook/chapter2>; rel=previous"

    link = Link("/", "http://example.net/foo")
    assert link.as_header() == '</>; rel="http://example.net/foo"'

    link = Link("/terms", "copyright", anchor="#foo")
    assert link.as_header() == '</terms>; rel=copyright; anchor="#foo"'
