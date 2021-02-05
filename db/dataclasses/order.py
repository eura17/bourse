from typing import Union
import datetime as dt

from db.dataclasses.ordertrademixin import OrderTradeMixin
from db.errors.executionvolumeerror import ExecutionVolumeError


class Order(OrderTradeMixin):
    __slots__ = (
        '__order_no',
        '__real_order_no',
        '__ticker',
        '__operation',
        '__type',
        '__datetime',
        '__action',
        '__price',
        '__volume',
        '__robot'
    )

    def __init__(self,
                 ticker: str,
                 operation: str,
                 order_type: str,
                 datetime: Union[dt.datetime, float],
                 action: str,
                 price: Union[int, float],
                 volume: int,
                 robot: str = None):
        self.__order_no = None
        self.__real_order_no = None
        self.__ticker = self._check_ticker(ticker)
        self.__operation = self._check_operation(operation)
        self.__type = self._check_type(order_type)
        self.__datetime = self._check_datetime(datetime)
        self.__action = self._check_action(action)
        self.__price = self._check_price(price)
        self.__volume = self._check_volume(volume)
        self.__robot = self._check_robot(robot)

    @property
    def order_no(self) -> int:
        return self.__order_no

    def set_order_no(self, value: int) -> None:
        self.__order_no = value

    @property
    def real_order_no(self) -> int:
        return self.__real_order_no

    def set_real_order_no(self, value: int) -> None:
        self.__real_order_no = value

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def operation(self) -> str:
        return self.__operation

    @property
    def type(self) -> str:
        return self.__type

    @property
    def datetime(self) -> dt.datetime:
        return self.__datetime

    @property
    def action(self) -> str:
        return self.__action

    @property
    def price(self) -> Union[int, float]:
        return self.__price

    @property
    def volume(self) -> int:
        return self.__volume

    @property
    def robot(self) -> str:
        return self.__robot

    def is_buy(self) -> bool:
        return self.__operation == 'buy'

    def is_sell(self) -> bool:
        return self.__operation == 'sell'

    def is_market(self) -> bool:
        return self.__type == 'market'

    def is_limit(self) -> bool:
        return self.__type == 'limit'

    def is_to_set(self) -> bool:
        return self.__action == 'set'

    def is_to_delete(self) -> bool:
        return self.__action == 'del'

    def is_executed(self) -> bool:
        return self.__volume == 0

    def execute(self, volume: int) -> None:
        if isinstance(volume, int) and volume <= self.volume:
            self.__volume -= volume
        else:
            raise ExecutionVolumeError
