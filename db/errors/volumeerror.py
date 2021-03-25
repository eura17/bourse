class VolumeError(ValueError):
    def __init__(self, volume):
        super().__init__(
            f'Volume must be int and greater than zero, not {volume}'
        )
