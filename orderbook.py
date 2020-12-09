from trade import Trade
TEST = 0

class OrderBook:
    def __init__(self,
                 ticker: str):
        self.ticker = ticker
        self.bids = {}
        self.asks = {}
        self.last_order_datetime = None
        self.last_trades = []
        self.total_deals = 0

    def get_data(self):
        ''' данные для роботов '''
        return {'max_bid_price': self.max_bid(),
                'max_bid_volume': self.bid_volume(self.max_bid()),
                'min_ask_price': self.min_ask(),
                'min_ask_volume': self.ask_volume(self.min_ask()),
                'datetime': self.last_order_datetime,
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

    def min_bid(self):
        return min(self.bids.keys())

    def max_bid(self):
        return max(self.bids.keys())

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
        return min(self.asks.keys())

    def max_ask(self):
        return max(self.asks.keys())

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
        orders.sort(key=lambda x: x.datetime)
        for order in orders:
            self.process_order(order)
        self.last_order_datetime = orders[-1].datetime

    def process_order(self,
                      order: 'Order'):
        if order.to_delete:
            self.delete_order(order)
        else:
            self.put_in_queue(order)

    def delete_order(self,
                     order: 'Order'):
        for market_side in (self.bids, self.asks):
            if order.price in market_side:
                for i in range(len(market_side[order.price])):
                    if order is market_side[order.price][i]:
                        market_side[order.price].pop(i)
                        return

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
        self.match_orders()

    def match_orders(self):
        if len(self.bids) == 0 or len(self.asks) == 0:
            return
        max_bid, min_ask = self.max_bid(), self.min_ask()
        #   cводит заявки, пока спрос выше предложения
        while max_bid >= min_ask:
            available_max_bid_volume = self.bid_volume(max_bid)
            available_min_ask_volume = self.ask_volume(min_ask)
            if available_max_bid_volume >= available_min_ask_volume:
                for i in range(len(self.bids[max_bid])):
                    last_bid = self.bids[max_bid][i]
                    last_ask = self.asks[min_ask][0]
                    volume = min(last_bid.lots, last_ask.lots)
                    last_ask.lots -= volume
                    if last_ask.lots == 0:
                        self.asks[min_ask].pop(0)
                        if len(self.asks[min_ask]) == 0:
                            del self.asks[min_ask]
                            max_bid, min_ask = self.max_bid(), self.min_ask()
                            break
                    if last_bid.username is not None:
                        self.last_trades.append(Trade('buy', min_ask, volume,
                                                robot=last_bid.username))
                    if last_ask.username is not None:
                        self.last_trades.append(Trade('sell', min_ask, volume,
                                                robot=last_ask.username))
                    self.total_deals += 1
                del self.bids[max_bid]
            else:
                for i in range(len(self.asks[min_ask])):
                    last_ask = self.asks[min_ask][i]
                    last_bid = self.bids[max_bid][0]
                    volume = min(last_ask.lots, last_bid.lots)
                    last_bid.lots -= volume
                    if last_bid.lots == 0:
                        self.bids[max_bid].pop(0)
                        if len(self.bids[max_bid]) == 0:
                            del self.bids[max_bid]
                            max_bid, min_ask = self.max_bid(), self.min_ask()
                            break
                    if last_ask.username is not None:
                        self.last_trades.append(Trade('sell', min_ask, volume,
                                                robot=last_ask.username))
                    if last_bid.username is not None:
                        self.last_trades.append(Trade('buy', min_ask, volume,
                                                robot=last_bid.username))
                    self.total_deals += 1
                del self.asks[min_ask]

            max_bid, min_ask = self.max_bid(), self.min_ask()


if __name__ == '__main__':
    o = OrderBook('SBER')
