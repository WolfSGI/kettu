from kettu.http.headers import Ranges


def test_range():

    rg = Ranges.from_string("bytes=0-1023")
    assert len(rg.values) == 1
    assert rg.unit == 'bytes'
    assert rg.values == (
        (0, 1023),
    )

    rg = Ranges.from_string("bytes=-1023")
    assert len(rg.values) == 1
    assert rg.unit == 'bytes'
    assert rg.values == (
        (-1023, -1),
    )

    rg = Ranges.from_string("knots=42-")
    assert len(rg.values) == 1
    assert rg.unit == 'knots'
    assert rg.values == (
        (42, -1),
    )


def test_ranges():
    rg = Ranges.from_string("bytes=500-999, 1000-1499")
    assert len(rg.values) == 2
    assert rg.unit == 'bytes'
    assert rg.values == ((500, 999), (1000, 1499))

    rg = Ranges.from_string("bytes=0-499,1000-,500-999")
    assert len(rg.values) == 3
    assert rg.unit == 'bytes'
    assert rg.values == ((0, 499), (1000, -1), (500, 999))

    rg = Ranges.from_string("bytes=0-4,90-99,5-75,100-199,101-102")
    assert len(rg.values) == 5
    assert rg.unit == 'bytes'
    assert rg.values == ((0, 4), (90, 99), (5, 75), (100, 199), (101, 102))


def test_ranges_resolve():
    rg = Ranges.from_string("bytes=0-4,90-99,5-75,100-199,101-102")
    resolved = rg.resolve(150, merge=True)
    assert resolved.unit == "bytes"
    assert resolved.values == ((0, 75), (90, 149))

    rg = Ranges.from_string("bytes=-1,20-100,0-1,101-120")
    resolved = rg.resolve(150, merge=True)
    assert resolved.values == ((0, 1), (20, 120), (149, 149))
