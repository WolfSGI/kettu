from typing import NamedTuple


class ETag(NamedTuple):
    value: str
    weak: bool = False

    def __str__(self):
        return self.as_header()

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return tuple.__eq__(self, other)

    @classmethod
    def from_string(cls, value: str) -> 'ETag':
        weak = False
        if value.startswith(('W/', 'w/')):
            weak = True
            value = value[2:]

        # Etag value SHOULD be quoted.
        return cls(value.strip('"'), weak=weak)

    def compare(self, other: 'ETag') -> bool:
        return self.value == other.value and not (self.weak or other.weak)

    def as_header(self) -> str:
        if self.weak:
            return f'W/"{self.value}"'
        return f'"{self.value}"'

    @classmethod
    def caster(cls, value: "str | ETag"):
        if isinstance(value, ETag):
            return value.as_header()
        return cls(value).as_header()


class ETags(frozenset[ETag]):
    # IfMatch / IfMatchNone

    def as_header(self) -> str:
        return ','.join((etag.as_header() for etag in self))

    @classmethod
    def from_string(cls, header: str) -> frozenset[ETag]:
        if ',' not in header:
            header = header.strip()
            if header:
                etag = ETag.from_string(header)
                return cls((etag,))

        etags = []
        values = header.split(',')
        for value in values:
            value = value.strip()
            if value:
                etags.append(ETag.from_string(value))
        if not etags:
            raise ValueError()
        return cls(etags)

    @classmethod
    def caster(cls, value: "str | ETags"):
        if isinstance(value, ETags):
            return value.as_header()
        return cls.from_string(value).as_header()
