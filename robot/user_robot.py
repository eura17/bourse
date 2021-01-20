from typing import Union, NoReturn
from collections import namedtuple
import datetime as dt

from db import User
from errors import TimeFrameError, OperationError
from matchingengine import Order

Candle = namedtuple('Candle', ['open', 'high', 'low', 'close', 'volume'])


class UserRobot(User):
    DATETIME: dt.datetime = None
    TIMEFRAMES = {
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

    def __init__(self):
        super().__init__('robot', 'robot')

    @classmethod
    def set_datetime(cls, value: dt.datetime) -> NoReturn:
        cls.DATETIME = value

    def get_active_orders(self,
                          robot: str,
                          ticker: str,
                          operation: str = None) -> list[Order]:
        if operation not in {'buy', 'sell'} and operation is not None:
            raw_orders = self._conn.call(
                'get_active_orders',
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

    def get_asset(self,
                  robot: str,
                  asset: str) -> list[int, float]:
        return self._conn.call(
            'get_asset_from_account',
            (robot,
             asset)
        )[0]

    def get_all_assets(self, robot: str) -> dict[str, list[int, float]]:
        return self._conn.call(
            'get_all_assets_from_account',
            (robot, )
        )[0]

    def liquidation_cost(self, robot: str) -> Union[int, float]:
        return self._conn.call(
            'calculate_liquidation_cost',
            (robot,)
        )[0]

    def min_ask(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'min_ask_price',
            (ticker,)
        )[0]

    def max_bid(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'max_bid_price',
            (ticker,)
        )[0]

    def order_book(self, ticker: str) -> dict[str, list[int, float]]:
        bid_ask = self._conn.call(
            'get_order_book',
            (ticker,)
        )[0]
        order_book = {
            'bid': list(sorted(bid_ask['bids'].items(), reverse=True)),
            'ask': list(sorted(bid_ask['asks'].items()))
        }
        return order_book

    def last_price(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'get_last_trade_price',
            (ticker,)
        )[0]

    def candles(self,
                ticker: str,
                timeframe: str,
                n: int = 1) -> list[type(Candle)]:
        if timeframe not in timeframe:
            raise TimeFrameError(timeframe)
        tf = self.TIMEFRAMES[timeframe]
        minutes = self.DATETIME.hour * 60 + self.DATETIME.minute
        minutes -= minutes % (tf.seconds // 60)
        start_dt = dt.datetime(
            self.DATETIME.year,
            self.DATETIME.month,
            self.DATETIME.day,
            minutes // 60,
            minutes % 60
        )
        stop_dt = start_dt - n * tf
        raw_candles = self._conn.call(
            'get_candles',
            (ticker, stop_dt.timestamp(), tf.seconds)
        )[0]
        candles = []
        for raw_candle in raw_candles:
            candles.append(Candle(*raw_candle))
        return candles
