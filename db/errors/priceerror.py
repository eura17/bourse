class PriceError(ValueError):
    def __init__(self, price):
        super(PriceError, self).__init__(
            f'Price must be int or float and 0 if order_type is market or '
            f'greater than 0 if order_type is limit '
            f'and for trade price is always must be greater than zero, '
            f'not {price}'
        )
