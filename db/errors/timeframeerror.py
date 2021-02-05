class TimeFrameError(ValueError):
    def __init__(self, timeframe):
        super().__init__(
            f'Timeframe {timeframe} don\'t exist'
        )
