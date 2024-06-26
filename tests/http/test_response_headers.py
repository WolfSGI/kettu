import pytest
import hamcrest
from datetime import datetime
from kettu.http.response import ResponseHeaders, UNSET
from kettu.http.headers import ETag


def test_link_container():
    headers = ResponseHeaders()

    assert "Link" not in headers
    headers.links.add("http://example.com/TheBook/chapter2", "previous")
    assert len(headers) == 1
    assert list(headers.items()) == [
        ('Link', '<http://example.com/TheBook/chapter2>; rel=previous')
    ]

    headers.links.add("/", "next", anchor="#top")
    assert len(headers) == 1
    assert list(headers.items()) == [(
        'Link',
        '<http://example.com/TheBook/chapter2>; rel=previous, '
        '</>; rel=next; anchor="#top"'
    )]

    assert "Link" in headers
    del headers["Link"]
    assert len(headers) == 0
    assert list(headers.items()) == []


def test_location_property():
    headers = ResponseHeaders()
    assert headers.location is UNSET
    headers.location = "/somepath"
    assert headers.location == '/somepath'
    assert headers == {
        'Location': '/somepath'
    }
    headers.location = "http://search.co.uk/my query?param=песец"
    assert headers.location == (
        "http://search.co.uk/my%20query?param=%D0%BF%D0%B5%D1%81%D0%B5%D1%86"
    )
    assert len(headers) == 1


def test_etag_property():
    headers = ResponseHeaders()
    assert headers.etag is UNSET
    headers.etag = "whatever"
    assert headers.etag == '"whatever"'
    assert headers == {
        'Etag': '"whatever"'
    }
    del headers.etag
    assert headers == {}

    headers.etag = "whatever"
    headers.etag = "however"
    assert headers == {
        'Etag': '"however"'
    }

    headers.etag = ETag("some value", weak=True)
    assert headers.etag == 'W/"some value"'


def test_content_type_property():
    headers = ResponseHeaders()
    assert headers.content_type is UNSET
    headers.content_type = "application/json"
    assert headers.content_type == "application/json"
    assert headers == {
        'Content-Type': "application/json"
    }
    del headers.content_type
    assert headers == {}

    headers.content_type = "whatever"
    headers.content_type = "text/html; charset=UTF-8"
    assert headers == {
        'Content-Type': "text/html;charset=UTF-8"
    }


def test_expires_property():
    headers = ResponseHeaders()
    assert headers.expires is UNSET
    headers.expires = datetime(2024, 4, 4, 18, 7, 00)
    assert headers.expires == "Thu, 04 Apr 2024 18:07:00 GMT"
    assert headers == {
        'Expires': "Thu, 04 Apr 2024 18:07:00 GMT"
    }
    assert len(headers) == 1
    del headers.expires
    assert headers == {}
    assert len(headers) == 0


def test_last_modified_property():
    headers = ResponseHeaders()
    assert headers.last_modified is UNSET
    headers.last_modified = datetime(2024, 4, 4, 18, 7, 00)
    assert headers.last_modified == "Thu, 04 Apr 2024 18:07:00 GMT"
    assert headers == {
        'Last-Modified': "Thu, 04 Apr 2024 18:07:00 GMT"
    }
    assert len(headers) == 1
    del headers.last_modified
    assert headers == {}
    assert len(headers) == 0


def test_empty_headers():
    headers = ResponseHeaders()
    assert list(headers.items()) == []
    assert len(headers) == 0


def test_add_headers():
    headers = ResponseHeaders({'X-Header': 'test'})
    assert list(headers.items()) == [('X-Header', 'test')]
    assert len(headers) == 1

    headers.add('X-Header', 'Another test')
    assert list(headers.items()) == [
        ('X-Header', 'test, Another test')
    ]
    assert len(headers) == 1


def test_headers_idempotency():
    headers = ResponseHeaders({'X-Header': 'test'})
    assert ResponseHeaders(headers) is headers


def test_headers_update():
    headers = ResponseHeaders({'X-Header': 'test'})
    headers.update({'X-Header': 'foo'})
    assert headers["x-header"] == "foo"

    headers.update({'Whatever': '1'})
    assert headers["whatever"] == "1"


def test_response_cookies():
    headers = ResponseHeaders()
    assert len(headers) == 0
    assert "Set-Cookies" not in headers

    headers.cookies.set('test', "{'this': 'is json'}")
    assert len(headers) == 1
    assert 'test' in headers.cookies
    assert list(headers.items()) == [
        ('Set-Cookie', 'test="{\'this\': \'is json\'}"; Path=/')
    ]
    assert list(headers) == ['Set-Cookie']
    assert "Set-Cookie" in headers

    del headers["Set-Cookie"]
    assert len(headers) == 0
    assert list(headers.items()) == []
    assert list(headers) == []


def test_headers_init():
    """Coalescence of headers does NOT garanty order of headers.
    It garanties the order of the header values, though.
    """
    headers = ResponseHeaders([
        ('X-Header', 'test'),
        ('X-Robots-Tag', 'noarchive'),
        ('X-Robots-Tag', 'google: noindex, nosnippet')
    ])

    hamcrest.assert_that(
        list(headers.items()),
        hamcrest.contains_inanyorder(
            ('X-Header', 'test'),
            ('X-Robots-Tag', 'noarchive, google: noindex, nosnippet'),
        )
    )

    headers.add('X-Robots-Tag', 'otherbot: noindex')
    hamcrest.assert_that(
        list(headers.items()),
        hamcrest.contains_inanyorder(
            ('X-Header', 'test'),
            ('X-Robots-Tag', ('noarchive, google: noindex, nosnippet, '
                               'otherbot: noindex')),
        )
    )

    assert list(headers) == ['X-Header', "X-Robots-Tag"]


def test_headers_coalescence_with_cookies_no_direct_assignation():
    headers = ResponseHeaders()
    headers.cookies.set('test', "{'this': 'is json'}")
    headers.add('X-Robots-Tag', 'otherbot: noindex')

    hamcrest.assert_that(
        list(headers.items()),
        hamcrest.contains_inanyorder(
            ('X-Robots-Tag', 'otherbot: noindex'),
            ('Set-Cookie', 'test="{\'this\': \'is json\'}"; Path=/')
        )
    )

    with pytest.raises(KeyError):
        headers.add('Set-Cookie', 'other=foobar')
