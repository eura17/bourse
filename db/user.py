from typing import NoReturn, Union
from abc import ABC
import datetime as dt

import tarantool

from db.dataclasses import Order, Trade, Candle
from db.dataclasses.ordertrademixin import OrderTradeMixin
from db.errors import OperationError, TimeFrameError, TickerError


class User(ABC):
    __HOST = None
    __PORT = None

    __TIMEFRAMES = {
        '1m': dt.timedelta(seconds=1),
        '2m': dt.timedelta(seconds=2),
        '3m': dt.timedelta(minutes=3),
        '4m': dt.timedelta(minutes=4),
        '5m': dt.timedelta(minutes=5),
        '6m': dt.timedelta(minutes=6),
        '10m': dt.timedelta(minutes=10),
        '15m': dt.timedelta(minutes=15),
        '20m': dt.timedelta(minutes=20),
        '30m': dt.timedelta(minutes=30),
        '1h': dt.timedelta(hours=1)
    }

    def __init__(self,
                 user: str = None,
                 password: str = None):
        self.__conn = tarantool.connect(
            self.__HOST,
            self.__PORT,
            user,
            password
        )

    @classmethod
    def set_host(cls, value: str) -> NoReturn:
        cls.__HOST = value

    @classmethod
    def set_port(cls, value: int) -> NoReturn:
        cls.__PORT = value

    @staticmethod
    def _set_tickers(tickers):
        OrderTradeMixin.set_tickers(tickers)

    @staticmethod
    def _set_robots(robots):
        OrderTradeMixin.set_robots(robots)

    def _create_order_log_space(self) -> NoReturn:
        self.__conn.call(
            'create_order_log_space'
        )

    def _add_order_to_order_log(self, order: Order) -> NoReturn:
        order_no = self.__conn.call(
            'add_order_to_order_log',
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

    def _save_order_log(self, path: str) -> NoReturn:
        ...

    def _create_order_book_spaces(self, ticker: str) -> NoReturn:
        self.__conn.call(
            'create_order_book_spaces',
            (ticker,)
        )

    def _add_order_to_order_book(self, order: Order) -> NoReturn:
        self.__conn.call(
            'add_order_to_order_book',
            (order.ticker,
             order.operation,
             order.order_no,
             order.real_order_no,
             order.datetime.timestamp(),
             order.price,
             order.volume,
             order.robot)
        )

    def _update_order_in_order_book(self, order: Order) -> NoReturn:
        self.__conn.call(
            'update_order_in_order_book',
            (order.ticker, order.operation, order.order_no, order.volume)
        )

    def _delete_order_from_order_book(self, order: Order) -> NoReturn:
        self.__conn.call(
            'delete_order_from_order_book',
            (order.ticker, order.operation, order.order_no, order.volume)
        )

    def _is_counter_orders_exist_in_order_book(self, order: Order) -> bool:
        return self.__conn.call(
            'is_counter_orders_exist_in_order_book',
            (order.ticker, order.operation)
        )[0]

    def _is_order_intersects_order_book(self, order: Order) -> bool:
        return self.__conn.call(
            'is_order_intersects_order_book',
            (order.ticker, order.operation, order.price)
        )[0]

    def _get_min_ask_price_from_order_book(self, ticker: str) \
            -> Union[int, float, None]:
        return self.__conn.call(
            'get_min_ask_price_from_order_book',
            (ticker,)
        )[0]

    def _get_min_ask_order_from_order_book(self, ticker: str) -> Order:
        min_ask_order = self.__conn.call(
            'get_min_ask_order_from_order_book',
            (ticker,)
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

    def _get_max_bid_price_from_order_book(self, ticker: str) \
            -> Union[int, float, None]:
        return self.__conn.call(
            'get_max_bid_price_from_order_book',
            (ticker,)
        )[0]

    def _get_max_bid_order_from_order_book(self, ticker: str) -> Order:
        max_bid_order = self.__conn.call(
            'get_max_bid_order_from_order_book',
            (ticker,)
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

    def _get_active_orders_from_order_book(self,
                                           robot: str,
                                           ticker: str,
                                           operation: str = None) \
            -> list[Order]:
        if operation in OrderTradeMixin().operations or operation is None:
            raw_orders = self.__conn.call(
                'get_active_orders_from_order_book',
                (robot, ticker, operation)
            )
            orders = []
            for raw_order in raw_orders:
                order = Order(
                    raw_order[2],
                    raw_order[3],
                    raw_order[4],
                    dt.datetime.fromtimestamp(raw_order[5]),
                    raw_order[6],
                    raw_order[7],
                    raw_order[8],
                    raw_order[9]
                )
                order.set_order_no(raw_order[0])
                order.set_real_order_no(raw_order[1])
                orders.append(order)
            return orders
        else:
            raise OperationError(operation)

    def _get_order_book(self, ticker: str) \
            -> dict[str, list[tuple[int, float]]]:
        bid_ask = self.__conn.call(
            'get_order_book',
            (ticker,)
        )[0]
        order_book = {
            'bid': list(sorted(bid_ask['bids'].items(), reverse=True)),
            'ask': list(sorted(bid_ask['asks'].items()))
        }
        return order_book

    def _create_trade_log_space(self) -> NoReturn:
        self.__conn.call(
            'create_trade_log_space'
        )

    def _add_trade_to_trade_log(self,
                                trade: Trade) -> NoReturn:
        self.__conn.call(
            'add_trade_to_trade_log',
            (trade.ticker,
             trade.datetime.timestamp(),
             trade.buy_order_no,
             trade.buyer_robot,
             trade.sell_order_no,
             trade.seller_robot,
             trade.price,
             trade.volume)
        )

    def _save_trade_log(self, path: str) -> NoReturn:
        ...

    def _get_last_trade_price_from_trade_log(self, ticker: str) \
            -> Union[int, float, None]:
        return self.__conn.call(
            'get_last_trade_price_from_trade_log',
            (ticker,)
        )[0]

    def _get_candles_from_trade_log(self,
                                    ticker: str,
                                    timeframe: str,
                                    datetime: dt.datetime,
                                    n: int = 1) -> list[type(Candle)]:
        if timeframe not in self.__TIMEFRAMES:
            raise TimeFrameError(timeframe)
        tf = self.__TIMEFRAMES[timeframe]
        minutes = datetime.hour * 60 + datetime.minute
        minutes -= minutes % (tf.seconds // 60)
        start_dt = dt.datetime(
            datetime.year,
            datetime.month,
            datetime.day,
            minutes // 60,
            minutes % 60
        )
        stop_dt = start_dt - n * tf
        raw_candles = self.__conn.call(
            'get_candles_from_trade_log',
            (ticker, stop_dt.timestamp(), tf.seconds)
        )[0]
        candles = []
        for raw_candle in raw_candles:
            candles.append(Candle(*raw_candle))
        return candles

    def _create_account_space(self, robot: str) -> NoReturn:
        self.__conn.call(
            'create_account_space',
            (robot,)
        )

    def _add_asset_to_account(self,
                              robot: str,
                              asset: str,
                              price: Union[int, float] = 0,
                              volume: int = 0):
        self.__conn.call(
            'add_asset_to_account',
            (robot, asset, price, volume)
        )

    def _get_asset_from_account(self,
                                robot: str,
                                asset: str) -> list[int, float]:
        if asset in OrderTradeMixin().tickers or asset == 'CASH':
            return self.__conn.call(
                'get_asset_from_account',
                (robot, asset)
            )[0]
        else:
            raise TickerError(asset)

    def _get_all_assets_from_account(self, robot: str) \
            -> dict[str, tuple[int, float]]:
        return self.__conn.call(
            'get_all_assets_from_account',
            (robot,)
        )[0]

    def _change_asset_in_account(self,
                                 robot: str,
                                 asset: str,
                                 price: Union[int, float],
                                 volume: int) -> NoReturn:
        self.__conn.call(
            'change_asset_in_account',
            (robot, asset, price, volume)
        )

    def _get_liquidation_cost_for_account(self,
                                          robot: str) -> Union[int, float]:
        return self.__conn.call(
            'get_liquidation_cost_for_account',
            (robot,)
        )[0]
