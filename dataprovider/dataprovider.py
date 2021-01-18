from typing import Iterable, NoReturn
from abc import abstractmethod
import datetime as dt

from dataprovider.user_dataprovider import UserDataProvider
from matchingengine import Order


class DataProvider(UserDataProvider):
    @abstractmethod
    def get_dates(self) -> Iterable[dt.date]:
        pass

    @abstractmethod
    def get_tickers(self) -> Iterable[str]:
        pass

    @abstractmethod
    def get_trading_time_bounds(self, date: dt.date) -> tuple[dt.datetime,
                                                              dt.datetime]:
        pass

    @abstractmethod
    def prepare_to_load_orders_for_date(self, date: dt.date) -> NoReturn:
        pass

    @abstractmethod
    def get_orders(self,
                   start_dt: dt.datetime,
                   end_dt: dt.datetime) -> list[Order]:
        pass