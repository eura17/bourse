from abc import ABC, abstractmethod

from order import Order


class Robot(ABC):
    def __init__(self,
                 username: str):
        self.username = username
        self.orders = []
        self.data_from_order_book = None
        self.data_from_accountant = None
        self.new_actions = []

    def update(self,
               data_from_order_book: dict,
               orders: list,
               data_from_accountant: dict):
        self.data_from_order_book = data_from_order_book
        self.orders = orders
        self.data_from_accountant = data_from_accountant

    def get_bid(self,
                volume_too: bool = False) -> float or ():
        if volume_too:
            return self.data_from_order_book['max_bid_price'], \
                   self.data_from_order_book['max_bid_volume']
        return self.data_from_order_book['max_bid_price']

    def get_ask(self,
                volume_too: bool = False) -> float or ():
        if volume_too:
            return self.data_from_order_book['min_ask_price'], \
                   self.data_from_order_book['min_ask_volume']
        return self.data_from_order_book['min_ask_price']

    def get_current_balance(self):
        return self.data_from_accountant['balance']

    def get_current_net_position(self):
        return self.data_from_accountant['cnp_price'], \
               self.data_from_accountant['cnp_lots']

    def get_last_price(self):
        pass

    @staticmethod
    def format_price(price: float):
        return float(format(price, '.2f'))

    def get_active_orders(self):
        return self.orders

    def get_buy_orders(self):
        buy_orders = []
        for order in self.orders:
            if order.type == 'buy':
                buy_orders.append(order)
        return buy_orders

    def get_sell_orders(self):
        sell_orders = []
        for order in self.orders:
            if order.type == 'sell':
                sell_orders.append(order)
        return sell_orders

    def order_send(self,
                   operation: 'buy or sell',
                   order_type: 'limit or market',
                   lots: int,
                   price: float = None):
        self.new_actions.append(Order(operation,
                                      order_type,
                                      lots,
                                      price,
                                      self.username,
                                      self.data_from_order_book['datetime'],
                                      True,
                                      False))

    def order_delete(self,
                     order):
        order.to_delete = True
        self.new_actions.append(order)

    def order_change(self,
                     order,
                     price: float = None,
                     lots: float = None):
        self.order_delete(order)
        self.order_send(order.operation,
                          order.order_type,
                          lots or order.lots,
                          price or order.price)

    @abstractmethod
    def train(self, df):
        pass

    @abstractmethod
    def on_tick(self):
        pass
