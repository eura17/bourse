from typing import List

from matchingengine.matchingengine import MatchingEngine
from db.dataclasses import Order
from db.dataclasses import Trade


class DefaultMatchingEngine(MatchingEngine):
    def execute_delete_order(self, order: Order) -> List[Trade]:
        self.delete_order(order)
        return []

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
                self.order_intersects(order):
            trades.append(self.match_with_first_best_counter_order(order))
        if not order.is_executed():
            self.add_order(order)
        return trades

    def match_with_first_best_counter_order(self, order: Order) -> Trade:
        to_buy = order.is_buy()
        counter_order = self.min_ask_order(order.ticker) if to_buy \
            else self.max_bid_order(order.ticker)
        execution_price = counter_order.price
        execution_volume = min(order.volume, counter_order.volume)
        order.execute(execution_volume)
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
        return trade
