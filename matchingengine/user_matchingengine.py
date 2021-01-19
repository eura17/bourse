from typing import Union, NoReturn
import os
import datetime as dt

from db import User
from matchingengine.order import Order
from matchingengine.trade import Trade


class UserMatchingEngine(User):
    def __init__(self):
        super().__init__('matching_engine', 'matching_engine')

    def configure(self) -> NoReturn:
        path = f'{os.path.dirname(os.path.realpath(__file__))}\\lua'
        lua_files = os.listdir(path)
        for file in lua_files:
            with open(f'{path}\\{file}', 'r', encoding='utf8') as f:
                self._conn.eval(f.read().strip())

    def create_order_log(self) -> NoReturn:
        self._conn.call(
            'create_order_log_space',
            ()
        )

    def add_to_order_log(self, order: Order) -> NoReturn:
        order_no = self._conn.call(
            'add_to_order_log',
            (order.order_no,
             order.real_order_no,
             order.ticker,
             order.operation,
             order.type,
             order.datetime.timestamp(),
             order.action,
             order.price,
             order.volume,
             order.robot)
        )[0]
        order.set_order_no(order_no)

    def save_order_log(self, path: str) -> NoReturn:
        raise NotImplementedError

    def create_trade_log(self):
        self._conn.call(
            'create_trade_log_space',
            ()
        )

    def add_to_trade_log(self,
                         trade: Trade) -> NoReturn:
        self._conn.call(
            'add_to_trade_log',
            (trade.ticker,
             trade.datetime.timestamp(),
             trade.buy_order_no,
             trade.buyer_robot,
             trade.sell_order_no,
             trade.seller_robot,
             trade.price,
             trade.volume)
        )

    def save_trade_log(self, path: str) -> NoReturn:
        raise NotImplementedError

    def create_bid_ask_spaces(self, ticker: str) -> NoReturn:
        self._conn.call(
            'create_bid_ask_spaces',
            (ticker, )
        )

    def add_order(self, order: Order) -> NoReturn:
        self._conn.call(
            'add_order',
            (order.ticker,
             order.operation,
             order.order_no,
             order.real_order_no,
             order.datetime.timestamp(),
             order.price,
             order.volume,
             order.robot)
        )

    def update_order(self, order: Order) -> NoReturn:
        self._conn.call(
            'update_order',
            (order.ticker,
             order.operation,
             order.order_no,
             order.volume)
        )

    def delete_order(self, order: Order) -> NoReturn:
        self._conn.call(
            'delete_order',
            (order.ticker,
             order.operation,
             order.order_no,
             order.volume)
        )

    def counter_orders_exist(self, order: Order) -> bool:
        return self._conn.call(
            'counter_orders_exist',
            (order.ticker,
             order.operation)
        )[0]

    def min_ask_price(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'min_ask_price',
            (ticker,)
        )[0]

    def min_ask_order(self, ticker: str) -> Order:
        min_ask_order = self._conn.call(
            'min_ask_order',
            (ticker, )
        )[0]
        order = Order(
            min_ask_order[2],
            min_ask_order[3],
            min_ask_order[4],
            dt.datetime.fromtimestamp(min_ask_order[5]),
            min_ask_order[6],
            min_ask_order[7],
            min_ask_order[8],
            min_ask_order[9],
        )
        order.set_order_no(min_ask_order[0])
        order.set_real_order_no(min_ask_order[1])
        return order

    def max_bid_price(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'max_bid_price',
            (ticker, )
        )[0]

    def max_bid_order(self, ticker: str) -> Order:
        max_bid_order = self._conn.call(
            'max_bid_order',
            (ticker, )
        )[0]
        order = Order(
            max_bid_order[2],
            max_bid_order[3],
            max_bid_order[4],
            dt.datetime.fromtimestamp(max_bid_order[5]),
            max_bid_order[6],
            max_bid_order[7],
            max_bid_order[8],
            max_bid_order[9],
        )
        order.set_order_no(max_bid_order[0])
        order.set_real_order_no(max_bid_order[1])
        return order
