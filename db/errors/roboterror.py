class RobotError(ValueError):
    def __init__(self, robot):
        super().__init__(
            f'Robot {robot} don\'t exist'
        )
