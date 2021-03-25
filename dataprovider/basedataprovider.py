from typing import Iterable, Union
from abc import abstractmethod
import datetime as dt

from db import User
from db.dataclasses import Order


class BaseDataProvider(User):
    def __init__(self,
                 tickers: Iterable[str],
                 discreteness: dt.timedelta = dt.timedelta(seconds=1)):
        super().__init__('data_provider', 'data_provider')
        self.__tickers = set(tickers)
        self.__discreteness = discreteness
        self.__datetime = None

    @abstractmethod
    def next_orders(self) -> Union[Iterable[Order], None]: ...

    @property
    def tickers(self) -> Iterable[str]:
        return self.__tickers

    @property
    def discreteness(self):
        return self.__discreteness

    @property
    def datetime(self) -> dt.datetime:
        return self.__datetime

    @datetime.setter
    def datetime(self, value: Union[dt.datetime, None]) -> None:
        if value is None:
            self.__datetime = None
            return
        if value - self.discreteness == self.__datetime:
            self.__datetime = value
            return
        d_micro = int(self.__discreteness.total_seconds() * 10 ** 6)
        dt_micro = value.microsecond + \
            value.second * 10 ** 6 + \
            value.minute * 60 * 10 ** 6 + \
            value.hour * 60 * 60 * 10 ** 6
        dt_micro -= dt_micro % d_micro
        self.__datetime = value.replace(
            hour=dt_micro // 10 ** 6 // 60 // 60 % 24,
            minute=dt_micro // 10 ** 6 // 60 % 60,
            second=dt_micro // 10 ** 6 % 60,
            microsecond=dt_micro % 10 ** 6
        )

    def __iter__(self):
        return self

    def __next__(self) -> Iterable[Order]:
        orders = self.next_orders()
        if orders is None:
            self._off()
            raise StopIteration()
        else:
            self.datetime += self.discreteness
            return orders
