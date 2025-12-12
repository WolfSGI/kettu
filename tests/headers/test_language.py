from kettu.headers import Languages, Language
from kettu.headers.constants import Specificity

def test_language():
    lang = Language.from_string('en-EN;q=0.5')
    assert lang.language.language == "en"
    assert lang.language.territory == "EN"
    assert lang == "en-EN"
    assert lang.quality == 0.5

    lang = Language.from_string('en-EN ; q=0.555')
    assert lang.language.language == "en"
    assert lang.language.territory == "EN"
    assert lang == "en-EN"
    assert lang.quality == 0.555
    assert lang.as_header() == "en-EN;q=0.555"


def test_language_wildcard_comparison():
    lang = Language.from_string('*')
    assert lang.specificity == Specificity.NONSPECIFIC
    assert lang.language == None

    assert lang != 'en'
    assert lang.match('en')
    assert lang.match('en-US')


def test_language_partially_specific_comparison():
    lang = Language.from_string('en')
    assert lang.specificity == Specificity.PARTIALLY_SPECIFIC

    assert lang != 'en-US'
    assert lang.match('en')
    assert lang.match('en-US')
    assert not lang.match('fr')


def test_languages():
    langs = Languages.from_string(
        'en-EN;q=0.5, fr-FR;q=0.8, de; q=0.3, ru; q=0.0'
    )
    assert len(langs) == 3
    assert langs == ('fr-FR', 'en-EN', 'de')
    assert langs[0].quality == 0.8
    assert langs[1].quality == 0.5
    assert langs[2].quality == 0.3
    assert langs.as_header() == 'fr-FR;q=0.8,en-EN;q=0.5,de;q=0.3'

    langs = Languages.from_string("*;q=0.5, en-EN;q=0.5")
    assert len(langs) == 2
    assert langs == ('en-EN', '*')
    assert langs.as_header() == 'en-EN;q=0.5,*;q=0.5'


def test_language_negotiation():
    langs = Languages.from_string(
        'en-EN;q=0.5, fr-FR;q=0.8, de; q=0.3, ru; q=0.0'
    )
    assert langs.negotiate(('fr-FR', 'en-EN')) == 'fr-FR'
    assert langs.negotiate(('ru', 'de-DE')) == 'de-DE'

    langs = Languages.from_string('en-EN;q=0.5')
    assert langs.negotiate(('fr-FR', 'en')) == 'en'

    langs = Languages.from_string('fi-FI')
    assert langs.negotiate(('fr-FR', 'en')) is None
