from typing import Union, NoReturn
import datetime as dt

from matchingengine.ordertrademixin import OrderTradeMixin
from errors import (
    TickerError,
    OperationError,
    OrderTypeError,
    DateTimeError,
    ActionError,
    PriceError,
    VolumeError,
    RobotError,
    ExecutionVolumeError
)


class Order(OrderTradeMixin):
    __slots__ = [
        '_order_no',
        '_real_order_no',
        '_ticker',
        '_operation',
        '_type',
        '_datetime',
        '_action',
        '_price',
        '_volume',
        '_robot'
    ]

    _OPERATIONS = {'buy', 'sell'}
    _TYPES = {'market', 'limit'}
    _ACTIONS = {'set', 'delete'}

    def __init__(self,
                 ticker: str,
                 operation: str,
                 order_type: str,
                 datetime: Union[dt.datetime, float],
                 action: str,
                 price: Union[int, float],
                 volume: int,
                 robot: str = None):
        self._order_no = None
        self._real_order_no = None
        if ticker in self._TICKERS:
            self._ticker = ticker
        else:
            raise TickerError(ticker)
        if operation in self._OPERATIONS:
            self._operation = operation
        else:
            raise OperationError(operation)
        if order_type in self._TYPES:
            self._type = order_type
        else:
            raise OrderTypeError(order_type)
        if isinstance(datetime, dt.datetime):
            self._datetime = datetime
        else:
            raise DateTimeError(datetime)
        if action in self._ACTIONS:
            self._action = action
        else:
            raise ActionError(action)
        if isinstance(price, (int, float)) and \
                (self.type == 'market' and price == 0) or \
                (self.type == 'limit' and price > 0):
            self._price = price
        else:
            raise PriceError
        if isinstance(volume, int) and volume > 0:
            self._volume = volume
        else:
            raise VolumeError
        if robot in self._ROBOTS or robot is None:
            self._robot = robot
        else:
            raise RobotError(robot)

    @property
    def order_no(self) -> int:
        return self._order_no

    def set_order_no(self, value: int) -> NoReturn:
        self._order_no = value

    @property
    def real_order_no(self) -> int:
        return self._real_order_no

    def set_real_order_no(self, value: int):
        self._real_order_no = value

    @property
    def ticker(self) -> str:
        return self._ticker

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def type(self) -> str:
        return self._type

    @property
    def datetime(self) -> dt.datetime:
        return self._datetime

    @property
    def action(self) -> str:
        return self._action

    @property
    def price(self) -> Union[int, float]:
        return self._price

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def robot(self) -> str:
        return self._robot

    def is_buy(self) -> bool:
        return self._operation == 'buy'

    def is_sell(self) -> bool:
        return self._operation == 'sell'

    def is_market(self) -> bool:
        return self._type == 'market'

    def is_limit(self) -> bool:
        return self._type == 'limit'

    def is_to_set(self) -> bool:
        return self._action == 'set'

    def is_to_delete(self) -> bool:
        return self._action == 'delete'

    def is_executed(self) -> bool:
        return self._volume == 0

    def execute(self, volume: int) -> NoReturn:
        if isinstance(volume, int) and volume <= self.volume:
            self._volume -= volume
        else:
            raise ExecutionVolumeError
