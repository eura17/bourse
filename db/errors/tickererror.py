class TickerError(ValueError):
    def __init__(self, ticker):
        super(TickerError, self).__init__(
            f'Ticker {ticker} don\'t exist'
        )
