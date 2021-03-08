from typing import Dict, Union
from robot.baserobot import BaseRobot


class MACDRobot(BaseRobot):
    __DEFAULT_FAST_PERIOD = 16
    __DEFAULT_SLOW_PERIOD = 26
    __DEFAULT_SIGNAL_PERIOD = 9
    __DEFAULT_PERIODICITY = '1m'

    def __init__(self, options: Dict[str, Union[int, float]]):
        super().__init__('MACD')
        self.fast_period = options.get('fast_period',
                                       self.__DEFAULT_FAST_PERIOD)
        self.slow_period = options.get('slow_period',
                                       self.__DEFAULT_SLOW_PERIOD)
        self.signal_period = options.get('signal_period',
                                         self.__DEFAULT_SIGNAL_PERIOD)
        if (p := options.get('periodicity', self.__DEFAULT_PERIODICITY)) \
                in self.timeframes:
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
                    candles_fast = candles[-self.fast_period:]
                    fast_sma = 0
                    for candle in candles_fast:
                        fast_sma += candle.close / self.fast_period
                    candles_slow = candles[-self.slow_period:]
                    slow_sma = 0
                    for candle in candles_slow:
                        slow_sma += candle.close / self.slow_period
                    macd = fast_sma - slow_sma
                    if len(candles) >= self.n and \
                            len(self.macd) >= self.signal_period:
                        self.macd = self.macd[-self.signal_period:]
                        signal_sma = 0
                        for signal in self.macd:
                            signal_sma += signal / self.signal_period

                        lots = int(self.max_money_for_lot /
                                   self.last_trade_price(ticker))
                        if macd < signal_sma:
                            if self.balance(ticker)[1] >= 0:
                                self.order_set(ticker, 'sell', 'market', lots)
                        elif macd > signal_sma:
                            if self.balance(ticker)[1] <= 0:
                                self.order_set(ticker, 'buy', 'market', lots)

                    self.macd.append(macd)
