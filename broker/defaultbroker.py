from typing import Union, Iterable, Dict, Tuple
from collections import defaultdict

from broker.basebroker import BaseBroker
from robot import BaseRobot
from db.dataclasses import Order, Trade


class DefaultBroker(BaseBroker):
    __DEFAULT_START_ACCOUNT = 100_000
    __DEFAULT_LEVERAGE = 1
    __DEFAULT_COMMISSION_ABS = 0
    __DEFAULT_COMMISSION_PCT = 0

    def __init__(self,
                 robots: Iterable[BaseRobot],
                 tickers: Iterable[str],
                 accounts_settings: Dict[str,
                                         Dict[str,
                                              Union[int, float]]] = None):
        super().__init__(robots)
        accounts_settings = accounts_settings or {}
        self.accounts_settings = defaultdict(dict)
        for robot in robots:
            self.accounts_settings[robot.name]['start_account'] = \
                accounts_settings.get(robot.name, dict()).get(
                    'start_account',
                    self.__DEFAULT_START_ACCOUNT
                )
            self.accounts_settings[robot.name]['leverage'] = \
                accounts_settings.get(robot.name, dict()).get(
                    'leverage',
                    self.__DEFAULT_LEVERAGE
                )
            self.accounts_settings[robot.name]['commission_abs'] = \
                accounts_settings.get(robot.name, dict()).get(
                    'commission_abs',
                    self.__DEFAULT_COMMISSION_ABS
                )
            self.accounts_settings[robot.name]['commission_pct'] = \
                accounts_settings.get(robot.name, dict()).get(
                    'commission_pct',
                    self.__DEFAULT_COMMISSION_PCT
                ) / 100
            self.open_account(robot.name, tickers)

    @classmethod
    def set_default(cls,
                    start_account: Union[int, float] = None,
                    leverage: Union[int, float] = None,
                    commission_abs: Union[int, float] = None,
                    commission_pct: Union[int, float] = None):
        cls.__DEFAULT_START_ACCOUNT = start_account or \
            cls.__DEFAULT_START_ACCOUNT
        cls.__DEFAULT_LEVERAGE = leverage or cls.__DEFAULT_LEVERAGE
        cls.__DEFAULT_COMMISSION_ABS = commission_abs or \
            cls.__DEFAULT_COMMISSION_ABS
        cls.__DEFAULT_COMMISSION_PCT = commission_pct or \
            cls.__DEFAULT_COMMISSION_PCT

    def open_account(self,
                     robot: str,
                     tickers: Iterable[str]) -> None:
        self.create_account(robot)
        self.add_asset(robot, 'CASH', 1,
                       self.accounts_settings[robot]['start_account'])
        for ticker in tickers:
            self.add_asset(robot, ticker)
        self.create_equity_curve(robot)

    def validate_order(self, order: Order) -> bool:
        if order.is_to_delete():
            return True
        _, cash = self.get_asset(order.robot, 'CASH')
        to_buy = order.is_buy()
        sign = (-1) ** to_buy
        execution_price = order.price
        if order.is_market():
            execution_price = self.last_trade_price(order.ticker)
            if execution_price is None:
                max_bid = self.max_bid_price(order.ticker)
                min_ask = self.min_ask_price(order.ticker)
                if max_bid is None or min_ask is None:
                    return False
                execution_price = (max_bid + min_ask) / 2
            execution_price *= 1.01 if to_buy \
                else 0.99
        trade_cost = execution_price * order.volume * sign - \
            self.commission(order.robot, execution_price, order.volume)
        min_limit, max_limit = self.cash_limits(order.robot)
        return min_limit < cash + trade_cost < max_limit

    def register_trade(self,
                       robot: str,
                       trade: Trade) -> None:
        self.accrue_asset(robot, trade)
        self.accrue_cash(robot, trade)

    def accrue_asset(self,
                     robot: str,
                     trade: Trade) -> None:
        cnp, cnv = self.get_asset(robot, trade.ticker)
        sign = (-1) ** (trade.seller_robot == robot)
        dvol = trade.volume * sign
        if cnv * dvol == 0:
            price, volume = trade.price, dvol
        elif cnv * dvol > 0:
            price, volume = self.avco(cnp, cnv, trade.price, dvol)
        else:
            total_volume = cnv + dvol
            if cnv * total_volume == 0:
                price, volume = 0, 0
            elif cnv * total_volume > 0:
                price, volume = cnp, total_volume
            else:
                price, volume = trade.price, total_volume
        self.change_asset(robot, trade.ticker, price, volume)

    @staticmethod
    def avco(price0: Union[int, float],
             volume0: int,
             price1: Union[int, float],
             volume1: int) -> Tuple[float, int]:
        vol = volume0 + volume1
        avco = price0 * (volume0 / vol) + price1 * (volume1 / vol)
        return avco, vol

    def accrue_cash(self,
                    robot: str,
                    trade: Trade) -> None:
        _, cash = self.get_asset(robot, 'CASH')
        sign = (-1) ** (trade.buyer_robot == robot)
        trade_cost = trade.price * trade.volume * sign - \
            self.commission(robot, trade.price, trade.volume)
        self.change_asset(robot, 'CASH', 1, cash + trade_cost)

    def commission(self,
                   robot: str,
                   price: Union[int, float],
                   volume: Union[int, float]) -> Union[int, float]:
        raw_trade_cost = price * volume
        commission_pct = raw_trade_cost * \
            self.accounts_settings[robot]['commission_pct']
        commission_abs = self.accounts_settings[robot]['commission_abs']
        return commission_pct + commission_abs

    def cash_limits(self, robot: str) -> Tuple[int, float]:
        liq_cost = self.liquidation_cost(robot)
        min_limit = liq_cost * (1 - self.accounts_settings[robot]['leverage'])
        max_limit = liq_cost * (1 + self.accounts_settings[robot]['leverage'])
        return min_limit, max_limit
