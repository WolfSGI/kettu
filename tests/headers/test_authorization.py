from kettu.headers import Authorization, DigestAuthParams


def test_authorization_header():
    auth = Authorization.from_string('Bearer SomeTokenValue')
    assert auth == ('bearer', 'SomeTokenValue')

    auth = Authorization.from_string('  Bearer   SomeTokenValue')
    assert auth == ('bearer', 'SomeTokenValue')

    auth = Authorization.from_string(' Bearer   Some Token Value     ')
    assert auth == ('bearer', 'Some Token Value')


def test_digest_authorization_header():
    auth = Authorization.from_string("""Digest realm="testrealm@host.com",
               qop="auth,auth-int",
               nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
               opaque="5ccc069c403ebaf9f0171e9517f40e41"
    """)
    assert auth == (
        'digest',
        DigestAuthParams(
            realm='testrealm@host.com',
            nonce='dcd98b7102dd2f0e8b11d0f600bfb0c093',
            qop='auth,auth-int',
            opaque='5ccc069c403ebaf9f0171e9517f40e41'
        )
    )

    auth = Authorization.from_string("""Digest username="Mufasa",
               realm="testrealm@host.com",
               nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
               uri="/dir/index.html",
               qop=auth,
               nc=00000001,
               cnonce="0a4f113b",
               response="6629fae49393a05397450978507c4ef1",
               opaque="5ccc069c403ebaf9f0171e9517f40e41"
    """)

    assert auth == (
        'digest',
        DigestAuthParams(
            realm='testrealm@host.com',
            username='Mufasa',
            uri="/dir/index.html",
            nonce='dcd98b7102dd2f0e8b11d0f600bfb0c093',
            nc='00000001',
            cnonce='0a4f113b',
            qop='auth',
            response='6629fae49393a05397450978507c4ef1',
            opaque='5ccc069c403ebaf9f0171e9517f40e41'
        )
    )

    auth = Authorization.from_string("""Digest realm="api@example.org",
               qop="auth",
               algorithm=SHA-512-256,
               nonce="5TsQWLVdgBdmrQ0XsxbDODV+57QdFR34I9HAbC/RVvkK",
               opaque="HRPCssKJSGjCrkzDg8OhwpzCiGPChXYjwrI2QmXDnsOS",
               userhash=true
    """)
    assert auth == (
        'digest',
        DigestAuthParams(
            realm='api@example.org',
            algorithm='SHA-512-256',
            nonce='5TsQWLVdgBdmrQ0XsxbDODV+57QdFR34I9HAbC/RVvkK',
            qop='auth',
            opaque='HRPCssKJSGjCrkzDg8OhwpzCiGPChXYjwrI2QmXDnsOS',
            userhash='true'
        )
    )
