from typing import Protocol
from abc import abstractmethod
from kettu.http.request import Request
from kettu.http.response import Response, FileResponse
from kettu.pluggability import Installable


class URIResolver(Protocol):

    def finalize(self) -> None:
        pass

    @abstractmethod
    def resolve(self, request: Request) -> Response | FileResponse:
        raise NotImplementedError("this method needs to be overridden.")


class Application(Protocol):

    resolver: URIResolver

    def use(self, *components: Installable):
        for component in components:
            component.install(self)

    def finalize(self):
        pass
