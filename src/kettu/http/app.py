from abc import ABC, abstractmethod
from kettu.http.request import Request
from kettu.http.response import Response, FileResponse
from kettu.pluggability import Installable
from aioinject import Container


class Application(ABC):

    services: Container

    def use(self, *components: Installable):
        for component in components:
            component.install(self)

    @abstractmethod
    def endpoint(self, request: Request) -> Response | FileResponse:
        ...
