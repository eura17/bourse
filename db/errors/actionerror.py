class ActionError(ValueError):
    def __init__(self, action):
        super(ActionError, self).__init__(
            f'Action must be set or delete, not {action}'
        )
