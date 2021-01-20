from typing import NoReturn

from db import User


class UserDataProvider(User):
    def __init__(self):
        super().__init__('data_provider', 'data_provider')
