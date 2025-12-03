from inspect import Signature
from functools import cached_property, cache
from types import FunctionType
from typing import NamedTuple


class immutable_cached_property(cached_property):
    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        del instance.__dict__[self.attrname]


class Dependency(NamedTuple):
    name: str
    type_: type


@cache
def method_dependencies(
        method: FunctionType | type) -> list[Dependency]:
    sig = Signature.from_callable(method)
    return [Dependency(name=key, type_=value.annotation)
            for key, value in sig.parameters.items()]
