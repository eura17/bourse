class TickerError(ValueError):
    def __init__(self, ticker):
        super(TickerError, self).__init__(
            f'Ticker {ticker} don\'t exist'
        )


class OperationError(ValueError):
    def __init__(self, operation):
        super(OperationError, self).__init__(
            f'Operation must be buy or sell, not {operation}'
        )


class DateTimeError(ValueError):
    def __init__(self, datetime):
        super(DateTimeError, self).__init__(
            f'Datetime must be datetime.datetime, not {type(datetime)}'
        )


class OrderTypeError(ValueError):
    def __init__(self, order_type):
        super(OrderTypeError, self).__init__(
            f'Order type must be market or limit, not {order_type}'
        )


class ActionError(ValueError):
    def __init__(self, action):
        super(ActionError, self).__init__(
            f'Action must be set or delete, not {action}'
        )


class PriceError(ValueError):
    def __init__(self, price):
        super(PriceError, self).__init__(
            f'Price must be int or float and 0 if order_type is market or '
            f'greater than 0 if order_type is limit '
            f'and for trade price is always must be greater than zero, '
            f'not {price}'
        )


class VolumeError(ValueError):
    def __init__(self, volume):
        super(VolumeError, self).__init__(
            f'Volume must be int and greater than zero, not {volume}'
        )


class ExecutionVolumeError(ValueError):
    def __init__(self):
        super(ExecutionVolumeError, self).__init__(
            f'Execution volume must be int and '
            f'cannot be higher than order\'s volume'
        )


class RobotError(ValueError):
    def __init__(self, robot):
        super(RobotError, self).__init__(
            f'Robot {robot} don\'t exist'
        )


class TimeFrameError(ValueError):
    def __init__(self, timeframe):
        super(TimeFrameError, self).__init__(
            f'Timeframe {timeframe} don\'t exist'
        )
