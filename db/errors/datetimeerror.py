class DateTimeError(ValueError):
    def __init__(self, datetime):
        super(DateTimeError, self).__init__(
            f'Datetime must be datetime.datetime, not {type(datetime)}'
        )
