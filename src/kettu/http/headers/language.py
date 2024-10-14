from typing import Any, Union, Sequence
from langcodes import Language as LangCode
from kettu.http.headers.constants import WEIGHT_PARAM, Specificity


class Language:
    __slots__ = ("language", "quality", "specificity")

    quality: float
    language: LangCode | None
    specificity: Specificity

    def __init__(
            self,
            locale: str,
            quality: float = 1.0
    ):
        self.quality = quality
        if locale != "*":
            self.language = LangCode.get(locale)
            self.specificity = (
                Specificity.SPECIFIC if (
                    self.language.territory or self.language.script
                )
                else Specificity.PARTIALLY_SPECIFIC
            )
        else:
            self.language = None
            self.specificity = Specificity.NONSPECIFIC

    @classmethod
    def from_string(cls, value: str) -> 'Language':
        locale, _, rest = value.partition(';')
        rest = rest.strip()
        if rest:
            matched = WEIGHT_PARAM.match(rest)
            if not matched:
                raise ValueError()
            quality = float(matched.group(1))
            return cls(locale.strip(), quality)
        return cls(locale.strip())

    def __str__(self):
        if not self.language:
            return "*"
        return self.language.to_tag()

    def as_header(self):
        return f"{str(self)};q={self.quality}"

    @classmethod
    def caster(cls, value: str):
        return cls.from_string(value).as_header()

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Language):
            if self.quality == other.quality:
                return self.specificity > other.specificity
            return self.quality > other.quality
        raise TypeError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Language):
            return self.language == other.language
        if isinstance(other, str):
            return str(self) == other
        return False

    def match(self, other: Union[str, 'Language']) -> bool:
        if self.specificity == Specificity.NONSPECIFIC:
            return True

        if isinstance(other, str):
            language = LangCode.get(other)
        else:
            language = other.language

        if self.specificity == Specificity.PARTIALLY_SPECIFIC or not language.territory or not language.script:
            return language.language == self.language.language

        return language == self.language


class Languages(tuple[Language, ...]):

    def __new__(cls, values: Sequence[Language]):
        if values:
            return super().__new__(cls, sorted(values))
        return super().__new__(cls, (Language('*'),))

    def as_header(self):
        return ','.join((lang.as_header() for lang in self))

    @classmethod
    def caster(cls, value: str):
        return cls.from_string(value).as_header()

    @classmethod
    def from_string(cls, header: str, keep_null: bool = False):
        if ',' not in header:
            header = header.strip()
            if header:
                lang = Language.from_string(header)
                if not keep_null and not lang.quality:
                    raise ValueError()
                return cls((lang,))

        langs = []
        values = header.split(',')
        for value in values:
            value = value.strip()
            if value:
                lang = Language.from_string(value)
                if not keep_null and not lang.quality:
                    continue
                langs.append(lang)
        if not langs:
            raise ValueError()
        return cls(langs)

    def negotiate(self, supported: Sequence[str | Language]):
        if not self:
            if not supported:
                return None
            return supported[0]
        for accepted in self:
            for candidate in supported:
                if accepted.match(candidate):
                    return candidate
        return None
