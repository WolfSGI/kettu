from abc import ABC, abstractmethod
from typing import Any


class Header(ABC):

    @classmethod
    @abstractmethod
    def from_string(cls, value: str) -> 'Header':
        ...


    @abstractmethod
    def as_header(cls) -> str | bytes:
        ...
