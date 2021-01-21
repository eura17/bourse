from typing import NoReturn
from abc import ABC
import tarantool


class User(ABC):
    _HOST = None
    _PORT = None

    def __init__(self,
                 user: str = None,
                 password: str = None):
        self._conn = tarantool.connect(self._HOST, self._PORT, user, password)

    @classmethod
    def set_host(cls, value: str) -> NoReturn:
        cls._HOST = value

    @classmethod
    def set_port(cls, value: int) -> NoReturn:
        cls._PORT = value
