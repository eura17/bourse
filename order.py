class Order:
    def __init__(self,
                 operation: {'buy', 'sell'},
                 order_type: {'limit', 'market'},
                 lots: int,
                 price: float = None,
                 username: str = None,
                 datetime: 'datetime.datetime' = None,
                 is_by_robot: bool = False,
                 order_no: int = None,
                 to_delete: bool = False):
        self.operation = operation
        self.order_type = order_type
        self.lots = lots
        self.price = price
        self.username = username
        self.datetime = datetime
        self.is_by_robot = is_by_robot
        self.order_no = order_no
        self.to_delete = to_delete

    def __str__(self):
        return f'Order({self.operation}, {self.order_type}, ' \
               f'{self.lots}, {self.price})'

    def __repr__(self):
        return f'Order({self.operation}, {self.order_type}, {self.lots}, ' \
               f'price={self.price}, username={self.username}, ' \
               f'datetime={self.datetime.strftime("%H:%M:%S.%f")}, ' \
               f'is_by_robot={self.is_by_robot}, order_no={self.order_no}, ' \
               f'to_delete={self.to_delete}'
