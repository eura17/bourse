from typing import Union, List
import datetime as dt
from abc import abstractmethod

from db import User
from db.dataclasses import Order, Candle, OrderBook


class BaseRobot(User):
    __DATETIME: dt.datetime = None
    __del_order = 'del'
    __set_order = 'set'
    __slots__ = (
        '__name',
        '__orders',
        '__tmp_data'
    )

    def __init__(self, name: str):
        super().__init__('robot', 'robot')
        self.__name = name
        self.__orders = []
        self.__tmp_data = {}

    @classmethod
    def set_datetime(cls, value: dt.datetime) -> None:
        cls.__DATETIME = value

    @property
    def datetime(self) -> dt.datetime:
        return self.__DATETIME

    @property
    def name(self) -> str:
        return self.__name

    @property
    def orders(self) -> List[Order]:
        return self.__orders

    @property
    def tmp_data(self) -> dict:
        return self.__tmp_data

    @abstractmethod
    def training(self, training_data) -> None: ...

    @abstractmethod
    def trading(self) -> None: ...

    def reset(self) -> None:
        self.__orders = []

    def max_bid_price(self, ticker: str) -> Union[int, float]:
        return self._get_max_bid_price_from_order_book(ticker)

    def min_ask_price(self, ticker: str) -> Union[int, float]:
        return self._get_min_ask_price_from_order_book(ticker)

    def order_book(self, ticker: str) -> OrderBook:
        return self._get_order_book(ticker)

    def last_trade_price(self, ticker: str) -> Union[int, float]:
        return self._get_last_trade_price_from_trade_log(ticker)

    def candles(self,
                ticker: str,
                timeframe: str,
                n: int = 1) -> List[Candle]:
        return self._get_candles_from_trade_log(
            ticker,
            timeframe,
            self.__DATETIME,
            n
        )

    def balance(self, asset: str = None):
        if asset is None:
            return self._get_all_assets_from_account(self.name)
        else:
            return self._get_asset_from_account(self.name, asset)

    def liquidation_cost(self) -> Union[int, float]:
        return self._get_liquidation_cost_for_account(self.name)

    def active_orders(self, ticker: str, operation: str = None) -> List[Order]:
        return self._get_active_orders_from_order_book(self.name,
                                                       ticker,
                                                       operation)

    def order_set(self,
                  ticker: str,
                  operation: str,
                  order_type: str,
                  volume: int,
                  price: Union[int, float] = 0) -> None:
        order = Order(
            ticker,
            operation,
            order_type,
            self.__DATETIME,
            self.__set_order,
            price,
            volume,
            self.name
        )
        self.__orders.append(order)

    def order_delete(self,
                     order: Order,
                     volume: int = None) -> None:
        order_del = Order(
            order.ticker,
            order.operation,
            order.type,
            self.__DATETIME,
            self.__del_order,
            order.price,
            volume or order.volume,
            self.name
        )
        order_del.set_order_no(order.order_no)
        self.__orders.append(order_del)
