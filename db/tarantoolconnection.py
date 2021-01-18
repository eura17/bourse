from abc import ABC
import tarantool


class TarantoolConnection(ABC):
    _HOST = None
    _PORT = None

    def __init__(self,
                 user: str,
                 password: str):
        self._conn = tarantool.connect(self._HOST, self._PORT, user, password)

    @classmethod
    def set_host(cls, value: str):
        cls._HOST = value

    @classmethod
    def set_port(cls, value: int):
        cls._PORT = value
