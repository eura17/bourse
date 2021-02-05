class TickerError(ValueError):
    def __init__(self, ticker):
        super().__init__(
            f'Ticker {ticker} don\'t exist'
        )
