from typing import List, Dict, Union
import datetime as dt
import os

from db import TarantoolConnection
from dataprovider import MOEXDataProvider
from broker import DefaultBroker
from matchingengine import FIFOMatchingEngine
from marketplace import MarketPlace

from robot import *


BASE_PATH = os.path.dirname(os.path.realpath(__file__))
DATE_TO_FILE = {
    dt.date(2015, 12, 7): os.path.join(BASE_PATH, 'order_logs',
                                       'OrderLog20151207.txt'),
    dt.date(2015, 12, 8): os.path.join(BASE_PATH, 'order_logs',
                                       'OrderLog20151208.txt'),
    dt.date(2015, 12, 9): os.path.join(BASE_PATH, 'order_logs',
                                       'OrderLog20151209.txt'),
    dt.date(2015, 12, 10): os.path.join(BASE_PATH, 'order_logs',
                                        'OrderLog20151210.txt'),
    dt.date(2015, 12, 11): os.path.join(BASE_PATH, 'order_logs',
                                        'OrderLog20151211.txt')
}
STRATEGY_TO_ROBOT = {
    'MACD': MACDRobot
}


def _run(tickers: List[str],
         dates: List[dt.date],
         strategies: Dict[str, dict],
         start_account: Union[int, float] = 100_000,
         leverage: Union[int, float] = 3,
         commission_abs: Union[int, float] = 0,
         commission_pct: Union[int, float] = 0,
         discreteness: dt.timedelta = dt.timedelta(seconds=1)):
    robots = []
    for strategy in strategies:
        if strategy in STRATEGY_TO_ROBOT:
            robot = STRATEGY_TO_ROBOT[strategy](strategies[strategy])
            robots.append(robot)
    dates_files = {}
    for date in dates:
        if date in DATE_TO_FILE:
            dates_files[date] = DATE_TO_FILE[date]
    DefaultBroker.set_default(
        start_account,
        leverage,
        commission_abs,
        commission_pct
    )

    dp = MOEXDataProvider(dates_files, tickers, discreteness)
    me = FIFOMatchingEngine(tickers)
    br = DefaultBroker(robots, tickers)
    mp = MarketPlace(dp, me, br, robots)
    mp.start()


def run(tickers: List[str],
        dates: List[dt.date],
        strategies: Dict[str, dict],
        start_account: Union[int, float] = 100_000,
        leverage: Union[int, float] = 3,
        commission_abs: Union[int, float] = 0,
        commission_pct: Union[int, float] = 0,
        discreteness: dt.timedelta = dt.timedelta(seconds=1),
        port: int = 4444):
    with TarantoolConnection(port):
        _run(
            tickers,
            dates,
            strategies,
            start_account,
            leverage,
            commission_abs,
            commission_pct,
            discreteness
        )


def run_windows(tickers: List[str],
                dates: List[dt.date],
                strategies: Dict[str, dict],
                start_account: Union[int, float] = 100_000,
                leverage: Union[int, float] = 3,
                commission_abs: Union[int, float] = 0,
                commission_pct: Union[int, float] = 0,
                discreteness: dt.timedelta = dt.timedelta(seconds=1),
                host: str = 'localhost',
                port: int = 4444,
                user: str = 'admin',
                password: str = 'admin'):
    TarantoolConnection.migrate(host, port, user, password)
    _run(
        tickers,
        dates,
        strategies,
        start_account,
        leverage,
        commission_abs,
        commission_pct,
        discreteness
    )
