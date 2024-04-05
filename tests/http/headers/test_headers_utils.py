from kettu.http.headers import utils


def test_encode_uri():
    uri = "http://www.mysite.com/a file with spaces.html"
    assert utils.encode_uri(uri) == (
        "http://www.mysite.com/a%20file%20with%20spaces.html"
    )

    uri = "http://test.fr/url!/éléphant?search=gris & africain"
    assert utils.encode_uri(uri) == (
        "http://test.fr/url%21/%C3%A9l%C3%A9phant?search=gris%20%26%20africain"
    )
