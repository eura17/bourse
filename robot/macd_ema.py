from typing import Dict, Union
from robot.baserobot import BaseRobot


class MACDEMARobot(BaseRobot):
    __DEFAULT_FAST_PERIOD = 16
    __DEFAULT_SLOW_PERIOD = 26
    __DEFAULT_SIGNAL_PERIOD = 9
    __DEFAULT_PERIODICITY = '1m'

    def __init__(self, options: Dict[str, Union[int, float]]):
        super().__init__('MACD_EMA')
        self.fast_period = options.get('fast_period',
                                       self.__DEFAULT_FAST_PERIOD)
        self.slow_period = options.get('slow_period',
                                       self.__DEFAULT_SLOW_PERIOD)
        self.signal_period = options.get('signal_period',
                                         self.__DEFAULT_SIGNAL_PERIOD)
        p = options.get('periodicity', self.__DEFAULT_PERIODICITY)
        if p in self.timeframes:
            self.periodicity = p
        else:
            self.periodicity = self.__DEFAULT_PERIODICITY

        self.n = self.slow_period + self.signal_period
        self.macd = []

        self.max_money_for_lot = None

    def training(self, training_data) -> None:
        self.max_money_for_lot = self.liquidation_cost() / len(self.tickers)

    def trading(self) -> None:
        if self.datetime.second == 1:
            for ticker in self.tickers:
                candles = self.candles(ticker, self.periodicity, self.n)
                if len(candles) >= self.slow_period:
                    fast_sma = sum([c.close for c in candles[-self.fast_period//2:]]) / self.fast_period//2
                    slow_sma = sum([c.close for c in candles[-self.slow_period//2:]]) / self.slow_period//2
                    macd = fast_sma - slow_sma
                    if len(candles) >= self.n and \
                            len(self.macd) >= self.signal_period:
                        self.macd = self.macd[-self.signal_period:]
                        signal_sma = sum(self.macd[-self.signal_period//2:]) / self.signal_period//2

                        lots = 2 * int(self.max_money_for_lot /
                                       self.last_trade_price(ticker))
                        if macd < signal_sma:
                            if self.balance(ticker)[1] >= 0:
                                self.order_set(ticker, 'sell', 'market', lots)
                        elif macd > signal_sma:
                            if self.balance(ticker)[1] <= 0:
                                self.order_set(ticker, 'buy', 'market', lots)

                    self.macd.append(macd)
