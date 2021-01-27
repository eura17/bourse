class TimeFrameError(ValueError):
    def __init__(self, timeframe):
        super(TimeFrameError, self).__init__(
            f'Timeframe {timeframe} don\'t exist'
        )
