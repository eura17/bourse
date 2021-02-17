from typing import Union, Iterable, Dict, Tuple
from abc import abstractmethod

from db import User
from db.dataclasses import Order, Trade


class Broker(User):
    def __init__(self,
                 robots: Iterable[str]):
        super().__init__('broker', 'broker')
        self._set_robots(robots)

    @abstractmethod
    def validate_order(self, order: Order) -> bool: ...

    @abstractmethod
    def register_trade(self, robot: str, trade: Trade) -> None: ...

    def process_trade(self, trade: Trade) -> None:
        if trade.buyer_robot is not None:
            self.register_trade(trade.buyer_robot, trade)
        if trade.seller_robot is not None:
            self.register_trade(trade.seller_robot, trade)

    def create_account(self, robot: str) -> None:
        self._create_account_space(robot)

    def add_asset(self,
                  robot: str,
                  asset: str,
                  price: Union[int, float] = 0,
                  volume: Union[int, float] = 0) -> None:
        self._add_asset_to_account(robot, asset, price, volume)

    def get_asset(self,
                  robot: str,
                  asset: str) -> Tuple[int, float]:
        return self._get_asset_from_account(robot, asset)

    def get_all_assets(self, robot: str) -> Dict[str, Tuple[int, float]]:
        return self._get_all_assets_from_account(robot)

    def change_asset(self,
                     robot: str,
                     asset: str,
                     price: Union[int, float] = None,
                     volume: Union[int, float] = None) -> None:
        self._change_asset_in_account(robot, asset, price, volume)

    def create_equity_curve(self, robot: str) -> None:
        self._create_equity_curve_space(robot)

    def update_equity_curve(self, datetime: float, robot: str) -> None:
        self._update_equity_curve_space(datetime, robot)

    def liquidation_cost(self, robot: str) -> Union[int, float]:
        return self._get_liquidation_cost_for_account(robot)

    def last_trade_price(self, ticker: str) -> Union[int, float, None]:
        return self._get_last_trade_price_from_trade_log(ticker)

    def max_bid_price(self, ticker: str) -> Union[int, float, None]:
        return self._get_max_bid_price_from_order_book(ticker)

    def min_ask_price(self, ticker: str) -> Union[int, float, None]:
        return self._get_min_ask_price_from_order_book(ticker)
