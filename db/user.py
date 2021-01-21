from typing import NoReturn
from abc import ABC

import tarantool


class User(ABC):
    __HOST = None
    __PORT = None

    def __init__(self,
                 user: str = None,
                 password: str = None):
        self._conn = tarantool.connect(
            self.__HOST,
            self.__PORT,
            user,
            password
        )

    @classmethod
    def set_host(cls, value: str) -> NoReturn:
        cls.__HOST = value

    @classmethod
    def set_port(cls, value: int) -> NoReturn:
        cls.__PORT = value
