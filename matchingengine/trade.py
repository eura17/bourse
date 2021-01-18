from typing import Union
import datetime as dt

from matchingengine.ordertrademixin import OrderTradeMixin
from errors import (
    TickerError,
    DateTimeError,
    RobotError,
    PriceError,
    VolumeError
)


class Trade(OrderTradeMixin):
    __slots__ = [
        '_ticker',
        '_datetime',
        '_buy_order_no',
        '_buyer_robot',
        '_sell_order_no',
        '_seller_robot',
        '_price',
        '_volume'
    ]

    def __init__(self,
                 ticker: str,
                 datetime: dt.datetime,
                 buy_order_no: int,
                 buyer_robot: str or None,
                 sell_order_no: int,
                 seller_robot: str or None,
                 price: float or int,
                 volume: int):
        if ticker in self._TICKERS:
            self._ticker = ticker
        else:
            raise TickerError(ticker)
        if isinstance(datetime, dt.datetime):
            self._datetime = datetime
        else:
            raise DateTimeError(datetime)
        self._buy_order_no = buy_order_no
        if buyer_robot in self._ROBOTS or buyer_robot is None:
            self._buyer_robot = buyer_robot
        else:
            raise RobotError(buyer_robot)
        self._sell_order_no = sell_order_no
        if seller_robot in self._ROBOTS or seller_robot is None:
            self._seller_robot = seller_robot
        else:
            raise RobotError(seller_robot)
        if isinstance(price, (int, float)) and price > 0:
            self._price = price
        else:
            raise PriceError(price)
        if isinstance(volume, int) and volume > 0:
            self._volume = volume
        else:
            raise VolumeError(volume)

    @property
    def ticker(self) -> str:
        return self._ticker

    @property
    def datetime(self) -> dt.datetime:
        return self._datetime

    @property
    def buy_order_no(self) -> int:
        return self._buy_order_no

    @property
    def buyer_robot(self) -> str:
        return self._buyer_robot

    @property
    def sell_order_no(self) -> int:
        return self._sell_order_no

    @property
    def seller_robot(self) -> str:
        return self._seller_robot

    @property
    def price(self) -> Union[int, float]:
        return self._price

    @property
    def volume(self) -> int:
        return self._volume
