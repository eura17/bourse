class DateTimeError(ValueError):
    def __init__(self, datetime):
        super().__init__(
            f'Datetime must be datetime.datetime, not {type(datetime)}'
        )
