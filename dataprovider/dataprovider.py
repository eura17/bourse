from typing import Iterable, Tuple, List
from abc import abstractmethod
import datetime as dt

from db import User
from db.dataclasses import Order


class DataProvider(User):
    def __init__(self):
        super().__init__('data_provider', 'data_provider')

    @abstractmethod
    def get_dates(self) -> Iterable[dt.date]: ...

    @abstractmethod
    def get_tickers(self) -> Iterable[str]: ...

    @abstractmethod
    def get_trading_time_bounds(self, date: dt.date) -> Tuple[dt.datetime,
                                                              dt.datetime]: ...

    @abstractmethod
    def prepare_to_load_orders_for_date(self, date: dt.date) -> None: ...

    @abstractmethod
    def get_orders(self,
                   start_dt: dt.datetime,
                   end_dt: dt.datetime) -> List[Order]: ...
