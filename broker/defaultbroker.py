from typing import Union, Iterable
from collections import defaultdict

from broker.broker import Broker
from db.dataclasses import Order, Trade


class DefaultBroker(Broker):
    __DEFAULT_START_ACCOUNT = 100_000
    __DEFAULT_LEVERAGE = 1
    __DEFAULT_COMMISSION_ABS = 0
    __DEFAULT_COMMISSION_PCT = 0

    def __init__(self,
                 robots: Iterable[str],
                 tickers: Iterable[str],
                 accounts_settings: dict[str,
                                         dict[str,
                                              Union[int, float]]] = None):
        super().__init__(robots)
        accounts_settings = accounts_settings or {}
        self.accounts_settings = defaultdict(dict)
        for robot in robots:
            self.accounts_settings[robot]['start_account'] = \
                accounts_settings.get(robot, dict()).get(
                    'start_account',
                    self.__DEFAULT_START_ACCOUNT
                )
            self.accounts_settings[robot]['leverage'] = \
                accounts_settings.get(robot, {}).get(
                    'leverage',
                    self.__DEFAULT_LEVERAGE
                )
            self.accounts_settings[robot]['commission_abs'] = \
                accounts_settings.get(robot, {}).get(
                    'commission_abs',
                    self.__DEFAULT_COMMISSION_ABS
                )
            self.accounts_settings[robot]['commission_pct'] = \
                accounts_settings.get(robot, {}).get(
                    'commission_pct',
                    self.__DEFAULT_COMMISSION_PCT
                )
            self.open_account(robot,
                              tickers)

    def open_account(self,
                     robot: str,
                     tickers: Iterable[str]) -> None:
        self.create_account(robot)
        self.add_asset(robot, 'CASH', 1,
                       self.accounts_settings[robot]['start_account'])
        for ticker in tickers:
            self.add_asset(robot, ticker)

    def validate_order(self, order: Order) -> bool:
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
            price, volume = self.avco(cnp, cnv, trade.price, trade.volume)
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
             volume1: int) -> tuple[float, int]:
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

    def cash_limits(self, robot: str) -> tuple[int, float]:
        liq_cost = self.liquidation_cost(robot)
        min_limit = liq_cost * (1 - self.accounts_settings[robot]['leverage'])
        max_limit = liq_cost * (1 + self.accounts_settings[robot]['leverage'])
        return min_limit, max_limit
