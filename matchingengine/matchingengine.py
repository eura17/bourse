from typing import Iterable

from matchingengine.user_matchingengine import UserMatchingEngine
from matchingengine.ordertrademixin import OrderTradeMixin
from matchingengine.order import Order
from matchingengine.trade import Trade


class MatchingEngine(UserMatchingEngine):
    __slots__ = []

    def __init__(self,
                 tickers: Iterable[str],
                 robots: Iterable[str]):
        super().__init__()
        OrderTradeMixin.set_tickers(tickers)
        OrderTradeMixin.set_robots(robots)
        for ticker in tickers:
            self.create_bid_ask_spaces(ticker)

    def process_order(self, order: Order) -> [Trade]:
        self.add_to_order_log(order)
        if order.is_to_delete():
            self.delete_order(order)
            return []
        elif order.is_market():
            return self.execute_market_order(order)
        elif order.is_limit():
            return self.execute_limit_order(order)

    def execute_market_order(self, order: Order) -> [Trade]:
        trades = []
        while not order.is_executed() and \
                self.counter_orders_exist(order):
            trades.append(self.match_with_first_best_counter_order(order))
        return trades

    def execute_limit_order(self, order: Order) -> [Trade]:
        trades = []
        while not order.is_executed() and \
                self.counter_orders_exist(order) and \
                self.order_intersect(order):
            trades.append(self.match_with_first_best_counter_order(order))
        if not order.is_executed():
            self.add_order(order)
        return trades

    def order_intersect(self, order: Order) -> bool:
        return (order.is_buy() and
                self.min_ask_price(order.ticker) <= order.price) or \
               (order.is_sell() and
                self.max_bid_price(order.ticker) >= order.price)

    def match_with_first_best_counter_order(self, order: Order) -> Trade:
        to_buy = order.is_buy()
        counter_order = self.min_ask_order(order.ticker) if to_buy \
            else self.max_bid_order(order.ticker)
        execution_price = counter_order.price
        execution_volume = min(order.volume, counter_order.volume)
        order.execute(execution_volume)
        if counter_order.volume == execution_volume:
            self.delete_order(counter_order)
        else:
            counter_order.execute(execution_volume)
            self.update_order(counter_order)
        trade = Trade(
            order.ticker,
            order.datetime,
            order.order_no if to_buy else counter_order.order_no,
            order.robot if to_buy else counter_order.robot,
            counter_order.order_no if to_buy else order.order_no,
            counter_order.robot if to_buy else order.robot,
            execution_price,
            execution_volume
        )
        self.add_to_trade_log(trade)
        return trade
