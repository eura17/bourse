from trade import Trade
import datetime


class OrderBook:
    def __init__(self,
                 ticker: str):
        self.ticker = ticker
        self.bids = {}
        self.asks = {}
        self.last_tick_datetime = datetime.datetime(year=2020,
                                                    month=12,
                                                    day=11,
                                                    hour=9,
                                                    minute=59,
                                                    second=59)
        self.last_tick = None
        self.last_trades = []
        self.total_deals = 0

    def get_data(self):
        ''' данные для роботов '''
        return {'max_bid_price': self.max_bid(),
                'max_bid_volume': self.bid_volume(self.max_bid()),
                'min_ask_price': self.min_ask(),
                'min_ask_volume': self.ask_volume(self.min_ask()),
                'last_quote': self.last_tick,
                'datetime': self.last_tick_datetime,
                'min_bid': self.min_bid(),
                'max_ask': self.max_ask()}

    def get_robots_orders(self):
        ''' все ордера в стакане от роботов '''
        robots_orders = {}
        for market_side in (self.bids, self.asks):
            for price in market_side:
                for order in market_side[price]:
                    if order.username not in robots_orders:
                        robots_orders[order.username] = []
                    robots_orders[order.username].append(order)
        return robots_orders

    def get_last_trades(self):
        ''' последние совершенные СДЕЛКИ '''
        return self.last_trades

    def get_last_tick(self, time_too: bool = False):
        if time_too:
            return self.last_tick, self.last_tick_datetime
        return self.last_tick

    def min_bid(self):
        return min(self.bids.keys()) if len(self.bids.keys()) != 0 else None

    def max_bid(self):
        return max(self.bids.keys()) if len(self.bids.keys()) != 0 else None

    def bid_volume(self,
                   price: float):
        if price not in self.bids:
            return 0
        volume = 0
        for order in self.bids[price]:
            volume += order.lots
        return volume

    def all_bid_volume(self):
        volume = 0
        for price in self.bids:
            for order in self.bids[price]:
                volume += order.lots
        return volume

    def min_ask(self):
        return min(self.asks.keys()) if len(self.asks.keys()) != 0 else None

    def max_ask(self):
        return max(self.asks.keys()) if len(self.asks.keys()) != 0 else None

    def ask_volume(self,
                   price: float):
        if price not in self.asks:
            return 0
        volume = 0
        for order in self.asks[price]:
            volume += order.lots
        return volume

    def all_ask_volume(self):
        volume = 0
        for price in self.asks:
            for order in self.asks[price]:
                volume += order.lots
        return volume

    def register_orders(self,
                        orders: ['Order']):
        if len(orders) == 0:
            return
        self.last_trades = []
        for order in orders:
            self.process_order(order)
        self.last_tick_datetime = orders[0].datetime

    def register_trade(self,
                       buyer: str,
                       seller: str,
                       price: float,
                       lots: int):
        self.last_trades.append(Trade(buyer, seller, price, lots))
        self.last_tick = price
        self.total_deals += 1

    def process_order(self,
                      order: 'Order'):
        if order.to_delete:
            self.delete_order(order)
        elif order.order_type == 'market':
            self.execute_by_market(order)
        else:
            self.execute_or_put_in_queue(order)

    def delete_order(self,
                     order: 'Order'):
        if order.operation == 'buy':
            self.delete_order_from_bid(order)
        else:
            self.delete_order_from_ask(order)

    def delete_order_from_bid(self,
                              order: 'Order'):
        # ордер уже исполнен однозначно
        if order.price not in self.bids:
            return
        # если надо удалить ордер робота
        if order.is_by_robot:
            for i in range(len(self.bids[order.price])):
                current_order = self.bids[order.price][i]
                if current_order is order:
                    current_order.lots -= order.lots
                    if current_order.lots <= 0:
                        self.bids[order.price].pop(i)
                    return
        # если удаление ордера пришло из источника данных
        for i in range(len(self.bids[order.price])):
            current_order = self.bids[order.price][i]
            if current_order.order_no == order.order_no:
                self.bids[order.price].pop(i)
                return

    def delete_order_from_ask(self,
                              order: 'Order'):
        if order.price not in self.asks:
            return
        # если надо удалить ордер робота
        if order.is_by_robot:
            for i in range(len(self.asks[order.price])):
                current_order = self.asks[order.price][i]
                if current_order is order:
                    self.asks[order.price].pop(i)
                    return
        # если удаление ордера пришло из источника данных
        for i in range(len(self.asks[order.price])):
            current_order = self.asks[order.price][i]
            if current_order.order_no == order.order_no:
                current_order.lots -= order.lots
                if current_order.lots <= 0:
                    self.asks[order.price].pop(i)
                return

    def execute_by_market(self,
                          order: 'Order'):
        if order.operation == 'buy':
            self.execute_buy_market(order)
        else:
            self.execute_sell_market(order)

    def execute_buy_market(self,
                              order: 'Order'):
        for price in sorted(self.asks):
            last_executed = 0
            for i in range(len(self.asks[price])):
                counter_order = self.asks[price][i]
                volume = min(order.lots, counter_order.lots)
                order.lots -= volume
                counter_order.lots -= volume
                self.register_trade(order.username,
                                    counter_order.username,
                                    counter_order.price,
                                    volume)
                if counter_order.lots == 0:
                    last_executed += 1
                if order.lots == 0:
                    break
            self.asks[price] = self.asks[price][last_executed:]
            if len(self.asks[price]) == 0:
                del self.asks[price]
            if order.lots == 0:
                return

    def execute_sell_market(self,
                               order: 'Order'):
        for price in sorted(self.bids, reverse=True):
            last_executed = 0
            for i in range(len(self.bids[price])):
                counter_order = self.bids[price][i]
                volume = min(order.lots, counter_order.lots)
                order.lots -= volume
                counter_order.lots -= volume
                self.register_trade(counter_order.username,
                                    order.username,
                                    counter_order.price,
                                    volume)
                if counter_order.lots == 0:
                    last_executed += 1
                if order.lots == 0:
                    break
            self.bids[price] = self.bids[price][last_executed:]
            if len(self.bids[price]) == 0:
                del self.bids[price]
            if order.lots == 0:
                return

    def execute_or_put_in_queue(self,
                                order: 'Order'):
        if order.operation == 'buy':
            self.execute_buy_limit(order)
        else:
            self.execute_sell_limit(order)

    def execute_buy_limit(self,
                          order: 'Order'):
        if len(self.asks) == 0:
            self.put_in_queue(order)
            return
        min_ask = self.min_ask()
        while min_ask <= order.price and order.lots != 0:
            last_executed = 0
            for i in range(len(self.asks[min_ask])):
                counter_order = self.asks[min_ask][i]
                volume = min(order.lots, counter_order.lots)
                order.lots -= volume
                counter_order.lots -= volume
                self.register_trade(order.username,
                                    counter_order.username,
                                    min_ask,
                                    volume)
                if counter_order.lots == 0:
                    last_executed += 1
                if order.lots == 0:
                    break
            self.asks[min_ask] = self.asks[min_ask][last_executed:]
            if len(self.asks[min_ask]) == 0:
                del self.asks[min_ask]
            if len(self.asks) == 0:
                if order.lots != 0:
                    self.put_in_queue(order)
                return
            min_ask = self.min_ask()
        else:
            if order.lots != 0:
                self.put_in_queue(order)

    def execute_sell_limit(self,
                           order: 'Order'):
        if len(self.bids) == 0:
            self.put_in_queue(order)
            return
        max_bid = self.max_bid()
        while max_bid >= order.price and order.lots != 0:
            last_executed = 0
            for i in range(len(self.bids[max_bid])):
                counter_order = self.bids[max_bid][i]
                volume = min(order.lots, counter_order.lots)
                order.lots -= volume
                counter_order.lots -= volume
                self.register_trade(counter_order.username,
                                    order.username,
                                    max_bid,
                                    volume)
                if counter_order.lots == 0:
                    last_executed += 1
                if order.lots == 0:
                    break
            self.bids[max_bid] = self.bids[max_bid][last_executed:]
            if len(self.bids[max_bid]) == 0:
                del self.bids[max_bid]
            if len(self.bids) == 0:
                if order.lots != 0:
                    self.put_in_queue(order)
                return
            max_bid = self.max_bid()
        else:
            if order.lots != 0:
                self.put_in_queue(order)

    def put_in_queue(self,
                     order: 'Order'):
        if order.operation == 'buy':
            if order.price not in self.bids:
                self.bids[order.price] = []
            self.bids[order.price].append(order)
        else:
            if order.price not in self.asks:
                self.asks[order.price] = []
            self.asks[order.price].append(order)


if __name__ == '__main__':
    o = OrderBook('SBER')
