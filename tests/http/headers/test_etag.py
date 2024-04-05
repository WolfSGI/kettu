from kettu.http.headers import ETag, ETags


def test_etag():
    etag = '"33a64df551425fcc55e4d42a148795d9f25f89d4"'
    e = ETag.from_string(etag)
    assert e == "33a64df551425fcc55e4d42a148795d9f25f89d4"
    assert e.weak is False
    assert e.as_header() == '"33a64df551425fcc55e4d42a148795d9f25f89d4"'

    etag = 'W/"0815"'
    e = ETag.from_string(etag)
    assert e == "0815"
    assert e.weak is True
    assert e.as_header() == 'W/"0815"'


def test_if_match():
    im = ETags.from_string('"33a64df551425fcc55e4d42a148795d9f25f89d4"')
    assert len(im) == 1
    assert im == {ETag("33a64df551425fcc55e4d42a148795d9f25f89d4")}
    assert "33a64df551425fcc55e4d42a148795d9f25f89d4" in im

    im = ETags((ETag("33a64df551425fcc55e4d42a148795d9f25f89d4", weak=True)))
    assert "33a64df551425fcc55e4d42a148795d9f25f89d4" in im

    im = ETags.from_string(
        '"33a64df551425fcc55e4d42a148795d9f25f89d4",' +
        '"ebeb4dbc1362d124452335a71286c21d",' +
        'W/"sdfe7vvc5sf68aaerv85"'
    )
    assert len(im) == 3
    assert im == {
        ETag("33a64df551425fcc55e4d42a148795d9f25f89d4"),
        ETag("ebeb4dbc1362d124452335a71286c21d"),
        ETag("sdfe7vvc5sf68aaerv85", weak=True)
    }
    assert im == {
        "33a64df551425fcc55e4d42a148795d9f25f89d4",
        "ebeb4dbc1362d124452335a71286c21d",
        "sdfe7vvc5sf68aaerv85"
    }
