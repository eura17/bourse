class Trade:
    def __init__(self,
                 operation: str,
                 price: float,
                 lots: int,
                 robot: str=None):
        self.operation = operation
        self.price = price
        self.lots = lots
        self.robot = robot
