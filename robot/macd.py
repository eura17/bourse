from robot.baserobot import BaseRobot


class MACDRobot(BaseRobot):
    def __init__(self, options):
        super().__init__('MACD')
        self.fast_period = options['fast_period']
        self.slow_period = options['slow_period']
        self.signal_period = options['signal_period']
        self.periodicity = options['periodicity']

        self.max_lots = None

    def training(self, training_data) -> None:
        self.max_lots = self.liquidation_cost() / len(self.tickers)

    def trading(self) -> None:
        ...
