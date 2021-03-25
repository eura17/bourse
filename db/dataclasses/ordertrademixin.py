from typing import Iterable, Union
import datetime as dt

from db.errors import (
    TickerError,
    OperationError,
    OrderTypeError,
    DateTimeError,
    ActionError,
    PriceError,
    VolumeError,
    RobotError
)


class OrderTradeMixin:
    __TICKERS = set()
    __ROBOTS = set()
    __OPERATIONS = {'buy', 'sell'}
    __TYPES = {'market', 'limit'}
    __ACTIONS = {'set', 'del'}

    @classmethod
    def set_tickers(cls, tickers: Iterable[str]) -> None:
        cls.__TICKERS = set(tickers)

    @property
    def tickers(self) -> set:
        return self.__TICKERS

    @classmethod
    def set_robots(cls, robots: Iterable[str]) -> None:
        cls.__ROBOTS = set(robots)

    @property
    def robots(self) -> set:
        return self.__ROBOTS

    @property
    def operations(self) -> set:
        return self.__OPERATIONS

    @property
    def types(self) -> set:
        return self.__TYPES

    @property
    def actions(self) -> set:
        return self.__ACTIONS

    def _check_ticker(self, value: str) -> str:
        if value in self.__TICKERS:
            return value
        else:
            raise TickerError(value)

    def _check_operation(self, value: str) -> str:
        if value in self.__OPERATIONS:
            return value
        else:
            raise OperationError(value)

    def _check_type(self, value: str) -> str:
        if value in self.__TYPES:
            return value
        else:
            raise OrderTypeError(value)

    @staticmethod
    def _check_datetime(value: dt.datetime) -> dt.datetime:
        if isinstance(value, dt.datetime):
            return value
        else:
            raise DateTimeError(value)

    def _check_action(self, value: str) -> str:
        if value in self.__ACTIONS:
            return value
        else:
            raise ActionError(value)

    @staticmethod
    def _check_price(value: Union[int, float]) -> Union[int, float]:
        if isinstance(value, (int, float)):
            return value
        else:
            raise PriceError(value)

    @staticmethod
    def _check_volume(value: int) -> int:
        if isinstance(value, int) and value > 0:
            return value
        else:
            raise VolumeError(value)

    def _check_robot(self, value: Union[str, None]) -> Union[str, None]:
        if value in self.__ROBOTS or value is None:
            return value
        else:
            raise RobotError(value)
