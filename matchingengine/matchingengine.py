from typing import Iterable, Union, List
import datetime as dt
from abc import abstractmethod

from db import User
from db.dataclasses import Order, Trade


class MatchingEngine(User):
    __slots__ = ()

    def __init__(self,
                 tickers: Iterable[str]):
        super().__init__('matching_engine', 'matching_engine')
        self._set_tickers(tickers)
        for ticker in tickers:
            self._create_order_book_spaces(ticker)

    @abstractmethod
    def execute_delete_order(self, order: Order) -> List[Trade]: ...

    @abstractmethod
    def execute_market_order(self, order: Order) -> List[Trade]: ...

    @abstractmethod
    def execute_limit_order(self, order: Order) -> List[Trade]: ...

    def process_order(self, order: Order) -> List[Trade]:
        self.save_order(order)
        if order.is_to_delete():
            return self.execute_delete_order(order)
        elif order.is_market():
            trades = self.execute_market_order(order)
            for trade in trades:
                self.save_trade(trade)
            return trades
        elif order.is_limit():
            trades = self.execute_limit_order(order)
            for trade in trades:
                self.save_trade(trade)
            return trades

    def create_tables(self) -> None:
        self._create_order_log_space()
        self._create_trade_log_space()

    def save_order(self, order: Order):
        self._add_order_to_order_log(order)

    def save_trade(self, trade: Trade):
        self._add_trade_to_trade_log(trade)

    def save_tables(self,
                    path: str,
                    date: dt.date) -> None:
        self._save_order_log(path, date)
        self._save_trade_log(path, date)

    def add_order(self, order: Order) -> None:
        self._add_order_to_order_book(order)

    def update_order(self, order: Order) -> None:
        self._update_order_in_order_book(order)

    def delete_order(self, order: Order) -> None:
        self._delete_order_from_order_book(order)

    def max_bid_price(self, ticker: str) -> Union[int, float]:
        return self._get_max_bid_price_from_order_book(ticker)

    def min_ask_price(self, ticker: str) -> Union[int, float]:
        return self._get_min_ask_price_from_order_book(ticker)

    def max_bid_order(self, ticker: str) -> Order:
        return self._get_max_bid_order_from_order_book(ticker)

    def min_ask_order(self, ticker: str) -> Order:
        return self._get_min_ask_order_from_order_book(ticker)

    def counter_orders_exist(self, order: Order) -> bool:
        return self._is_counter_orders_exist_in_order_book(order)

    def order_intersects(self, order: Order) -> bool:
        return self._is_order_intersects_order_book(order)
