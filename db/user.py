from typing import NoReturn
from abc import abstractmethod

from db.tarantoolconnection import TarantoolConnection


class User(TarantoolConnection):
    def __init__(self,
                 user: str,
                 password: str):
        super(User, self).__init__(user, password)
        self.configure()

    @abstractmethod
    def configure(self) -> NoReturn:
        pass
