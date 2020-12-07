class Order:
    def __init__(self,
                 operation: 'buy or sell or delete',
                 order_type: 'limit or market' = None,
                 lots: int = None,
                 price: float = None,
                 order_num: int = None):
        pass


class OrderBook:
    def __init__(self,
                 ticker: str):
        self.ticker = ticker
        self.bids = []
        self.asks = []

    def register_orders(self,
                        orders: []):
        # заполняем реальные заявки из данных
        #self.bids.extend(bids_to_add)
        #self.asks.extend(asks_to_add)
        #

        self.bids.sort(key=lambda x: x[0])
        self.asks.sort(key=lambda x: x[0], reverse=True)

    def update(self,
               event):
        pass


if __name__ == '__main__':
    o = OrderBook('SBER')
