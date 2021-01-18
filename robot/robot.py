from typing import NoReturn, Union
from abc import abstractmethod

from robot.user_robot import UserRobot
from errors import TickerError
from matchingengine import Order


class Robot(UserRobot):
    __slots__ = [
        '_name',
        '_orders',
        '_tmp_data'
    ]

    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._orders = []
        self._tmp_data = {}

    @property
    def datetime(self):
        return self.DATETIME

    @property
    def name(self) -> str:
        return self._name

    @property
    def orders(self) -> list[Order]:
        return self._orders

    @property
    def tmp_data(self) -> dict:
        return self._tmp_data

    @abstractmethod
    def training(self,
                 training_data) -> NoReturn:
        pass

    @abstractmethod
    def trading(self) -> NoReturn:
        pass

    def gather_orders(self) -> list[Order]:
        return self._orders

    def reset_orders(self) -> NoReturn:
        self._orders = []

    def order_set(self,
                  ticker: str,
                  operation: str,
                  order_type: str,
                  volume: int,
                  price: Union[int, float] = 0):
        order = Order(
                ticker,
                operation,
                order_type,
                self.DATETIME,
                'set',
                price,
                volume,
                self.name
            )
        self._orders.append(order)

    def order_delete(self, order: Order):
        order = Order(
                order.ticker,
                order.operation,
                order.type,
                self.DATETIME,
                'delete',
                order.price,
                order.volume,
                self.name
            )
        order.set_order_no(order.order_no)
        order.set_real_order_no(order.real_order_no)
        self._orders.append(order)

    def active_orders(self,
                      ticker: str,
                      operation: str) -> list[Order]:
        return self.get_active_orders(self.name, ticker, operation)

    def balance(self, asset: str = None) -> Union[list[int, float],
                                                  dict[str, list[int, float]]]:
        if asset is None:
            return self.get_all_assets(self.name)
        elif asset in Order.tickers or asset == 'CASH':
            return self.get_asset(self.name, asset)
        else:
            raise TickerError(asset)
