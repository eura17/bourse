class Robot:
    def __init__(self,
                 username: str):
        self.username = username
        self.positions = []
        self.orders = []

    def get_bid(self) -> float:
        pass

    def get_ask(self) -> float:
        pass

    def order_send(self,
                   operation: 'buy or sell',
                   order_type: 'limit or market',
                   lots: int,
                   price: float = None):
        pass

    def order_delete(self,
                     order):
        pass

