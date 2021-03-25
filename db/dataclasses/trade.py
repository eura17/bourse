from typing import Union
import datetime as dt

from db.dataclasses.ordertrademixin import OrderTradeMixin


class Trade(OrderTradeMixin):
    __slots__ = (
        '__ticker',
        '__datetime',
        '__buy_order_no',
        '__buyer_robot',
        '__sell_order_no',
        '__seller_robot',
        '__price',
        '__volume'
    )

    def __init__(self,
                 ticker: str,
                 datetime: dt.datetime,
                 buy_order_no: int,
                 buyer_robot: str or None,
                 sell_order_no: int,
                 seller_robot: str or None,
                 price: float or int,
                 volume: int):
        self.__ticker = self._check_ticker(ticker)
        self.__datetime = self._check_datetime(datetime)
        self.__buy_order_no = buy_order_no
        self.__buyer_robot = self._check_robot(buyer_robot)
        self.__sell_order_no = sell_order_no
        self.__seller_robot = self._check_robot(seller_robot)
        self.__price = self._check_price(price)
        self.__volume = self._check_volume(volume)

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def datetime(self) -> dt.datetime:
        return self.__datetime

    @property
    def buy_order_no(self) -> int:
        return self.__buy_order_no

    @property
    def buyer_robot(self) -> str:
        return self.__buyer_robot

    @property
    def sell_order_no(self) -> int:
        return self.__sell_order_no

    @property
    def seller_robot(self) -> str:
        return self.__seller_robot

    @property
    def price(self) -> Union[int, float]:
        return self.__price

    @property
    def volume(self) -> int:
        return self.__volume
