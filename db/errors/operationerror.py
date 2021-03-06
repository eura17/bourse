class OperationError(ValueError):
    def __init__(self, operation):
        super().__init__(
            f'Operation must be buy or sell, not {operation}'
        )
