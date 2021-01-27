class OrderTypeError(ValueError):
    def __init__(self, order_type):
        super(OrderTypeError, self).__init__(
            f'Order type must be market or limit, not {order_type}'
        )
