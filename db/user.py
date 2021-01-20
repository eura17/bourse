import tarantool

from db.tarantoolconnection import TarantoolConnection


class User(TarantoolConnection):
    def __init__(self,
                 user: str = None,
                 password: str = None):
        self._conn = tarantool.connect(self._HOST, self._PORT, user, password)
