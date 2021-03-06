class ExecutionVolumeError(ValueError):
    def __init__(self):
        super().__init__(
            f'Execution volume must be int and '
            f'cannot be higher than order\'s volume'
        )
