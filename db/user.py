from typing import Union, List, Dict, Tuple, Set, Iterable
from abc import ABC
import datetime as dt

import tarantool

from db.dataclasses import Order, Trade, Candle, OrderBook
from db.dataclasses.ordertrademixin import OrderTradeMixin
from db.errors import OperationError, TimeFrameError, TickerError


class User(ABC):
    __HOST = None
    __PORT = None

    __CHUNK_SIZE = 100_000

    __TIMEFRAMES = {
        '1m': dt.timedelta(minutes=1),
        '2m': dt.timedelta(minutes=2),
        '3m': dt.timedelta(minutes=3),
        '4m': dt.timedelta(minutes=4),
        '5m': dt.timedelta(minutes=5),
        '6m': dt.timedelta(minutes=6),
        '10m': dt.timedelta(minutes=10),
        '15m': dt.timedelta(minutes=15),
        '20m': dt.timedelta(minutes=20),
        '30m': dt.timedelta(minutes=30),
        '1h': dt.timedelta(hours=1),
        '2h': dt.timedelta(hours=2),
        '4h': dt.timedelta(hours=4),
        '8h': dt.timedelta(hours=8),
        '1d': dt.timedelta(days=1)
    }
    __TICKERS = set()

    def __init__(self,
                 user: str = None,
                 password: str = None):
        self.__conn = tarantool.connect(
            self.__HOST,
            self.__PORT,
            user,
            password
        )

    @property
    def timeframes(self) -> Dict[str, dt.timedelta]:
        return self.__TIMEFRAMES

    @property
    def tickers(self) -> Set[str]:
        return self.__TICKERS

    @classmethod
    def set_host(cls, value: str) -> None:
        cls.__HOST = value

    @classmethod
    def set_port(cls, value: int) -> None:
        cls.__PORT = value

    @classmethod
    def _set_tickers(cls, tickers: Iterable[str]):
        tickers = set(tickers)
        OrderTradeMixin.set_tickers(tickers)
        cls.__TICKERS |= tickers

    @staticmethod
    def _set_robots(robots):
        OrderTradeMixin.set_robots(robots)

    def _create_order_log_space(self) -> None:
        self.__conn.call(
            'create_order_log_space'
        )

    def _add_order_to_order_log(self, order: Order) -> None:
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

    def _save_order_log(self, path: str) -> None:
        headers = 'no,' \
                  'order_no,' \
                  'real_order_no,' \
                  'ticker,' \
                  'operation,' \
                  'type,' \
                  'datetime,' \
                  'action,price,' \
                  'volume,' \
                  'robot'
        total_orders = self.__conn.call(
            'get_amount_of_orders_in_order_log'
        )[0]
        processed_orders = 0
        with open(f'{path}/order_log.csv', 'w') as f:
            print(headers, file=f)
            while processed_orders <= total_orders:
                orders = self.__conn.call(
                    'get_orders_from_order_log',
                    (processed_orders, processed_orders + self.__CHUNK_SIZE)
                )[0]
                processed_orders += self.__CHUNK_SIZE
                for order in orders:
                    print(*order, sep=',', file=f)

    def _create_order_book_spaces(self, ticker: str) -> None:
        self.__conn.call(
            'create_order_book_spaces',
            (ticker,)
        )

    def _add_order_to_order_book(self, order: Order) -> None:
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

    def _update_order_in_order_book(self, order: Order) -> None:
        self.__conn.call(
            'update_order_in_order_book',
            (order.ticker, order.operation, order.order_no, order.volume)
        )

    def _delete_order_from_order_book(self, order: Order) -> None:
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
            -> List[Order]:
        if operation in OrderTradeMixin().operations or operation is None:
            raw_orders = self.__conn.call(
                'get_active_orders_from_order_book',
                (robot, ticker, operation)
            )[0]
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

    def _get_order_book(self, ticker: str) -> OrderBook:
        bid_ask = self.__conn.call(
            'get_order_book',
            (ticker,)
        )[0]
        order_book = OrderBook(
            bid=tuple(sorted(bid_ask['bids'].items(), reverse=True)),
            ask=tuple(sorted(bid_ask['asks'].items()))
        )
        return order_book

    def _create_trade_log_space(self) -> None:
        self.__conn.call(
            'create_trade_log_space'
        )

    def _add_trade_to_trade_log(self,
                                trade: Trade) -> None:
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

    def _save_trade_log(self, path: str) -> None:
        headers = 'trade_no,' \
                  'ticker,' \
                  'datetime,' \
                  'buy_order_no,' \
                  'buyer_robot,' \
                  'sell_order_no,' \
                  'seller_robot,' \
                  'price,' \
                  'volume'
        total_trades = self.__conn.call(
            'get_amount_of_trades_in_trade_log'
        )[0]
        processed_trades = 0
        with open(f'{path}/trade_log.csv', 'w') as f:
            print(headers, file=f)
            while processed_trades <= total_trades:
                trades = self.__conn.call(
                    'get_trades_from_trade_log',
                    (processed_trades, processed_trades + self.__CHUNK_SIZE)
                )[0]
                processed_trades += self.__CHUNK_SIZE
                for trade in trades:
                    print(*trade, sep=',', file=f)

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
                                    n: int = 1) -> List[Candle]:
        if timeframe not in self.__TIMEFRAMES:
            raise TimeFrameError(timeframe)
        real_n = n
        n += 1
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
        if len(candles) > real_n:
            return candles[-real_n:]
        return candles

    def _create_account_space(self, robot: str) -> None:
        self.__conn.call(
            'create_account_space',
            (robot,)
        )

    def _add_asset_to_account(self,
                              robot: str,
                              asset: str,
                              price: Union[int, float] = 0,
                              volume: int = 0) -> None:
        self.__conn.call(
            'add_asset_to_account',
            (robot, asset, price, volume)
        )

    def _get_asset_from_account(self,
                                robot: str,
                                asset: str) -> Tuple[float, int]:
        if asset in OrderTradeMixin().tickers or asset == 'CASH':
            return tuple(self.__conn.call(
                'get_asset_from_account',
                (robot, asset)
            )[0])
        else:
            raise TickerError(asset)

    def _get_all_assets_from_account(self, robot: str) \
            -> Dict[str, Tuple[int, float]]:
        return self.__conn.call(
            'get_all_assets_from_account',
            (robot,)
        )[0]

    def _change_asset_in_account(self,
                                 robot: str,
                                 asset: str,
                                 price: Union[int, float],
                                 volume: int) -> None:
        self.__conn.call(
            'change_asset_in_account',
            (robot, asset, price, volume)
        )

    def _get_liquidation_cost_for_account(self, robot: str) \
            -> Union[int, float]:
        return self.__conn.call(
            'get_liquidation_cost_for_account',
            (robot,)
        )[0]

    def _create_equity_curve_space(self, robot: str) -> None:
        self.__conn.call(
            'create_equity_curve_space',
            (robot,)
        )

    def _save_equity_curve(self, robot: str, path: str) -> None:
        headers = 'no, datetime, liquidation_cost'
        total_records = self.__conn.call(
            'get_amount_of_records_in_equity_curve',
            (robot,)
        )[0]
        processed_records = 0
        with open(f'{path}/equity_curve_{robot}.csv', 'w') as f:
            print(headers, file=f)
            while processed_records <= total_records:
                records = self.__conn.call(
                    'get_records_from_equity_curve',
                    (robot,
                     processed_records, processed_records + self.__CHUNK_SIZE)
                )[0]
                processed_records += self.__CHUNK_SIZE
                for record in records:
                    print(*record, sep=',', file=f)

    def _update_equity_curve_space(self, datetime: float, robot: str) -> None:
        self.__conn.call(
            'update_equity_curve_space',
            (datetime, robot)
        )

    def _off(self):
        self.__conn.call(
            'off'
        )
