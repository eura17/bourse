class RobotError(ValueError):
    def __init__(self, robot):
        super(RobotError, self).__init__(
            f'Robot {robot} don\'t exist'
        )
