from typing import Dict, Union
from robot.baserobot import BaseRobot


class RSIRobot(BaseRobot):
    __DEFAULT_PERIOD = 14
    __DEFAULT_PERIODICITY = '1m'

    def __init__(self, options: Dict[str, Union[int, float]]):
        super().__init__('RSI')
        self.period = options.get('RSI_period', self.__DEFAULT_PERIOD)
        if (p := options.get('periodicity', self.__DEFAULT_PERIODICITY)) \
                in self.timeframes:
            self.periodicity = p
        else:
            self.periodicity = self.__DEFAULT_PERIODICITY

        self.max_money_for_lot = None

    def training(self, training_data) -> None:
        self.max_money_for_lot = self.liquidation_cost() / len(self.tickers)

    def trading(self) -> None:
        if self.datetime.second == 1:
            for ticker in self.tickers:
                candles = self.candles(ticker, self.periodicity, self.period)
                if len(candles) >= self.period:
                    gain = 0
                    loss = 0
                    for i in range(1, len(candles)):
                        if candles[i].close > candles[i-1].close:
                            gain += candles[i].close - candles[i-1].close
                        else:
                            loss += candles[i-1].close - candles[i].close
                    avg_gain = gain / self.period
                    avg_loss = loss / self.period
                    if avg_loss != 0:
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                    else:
                        rsi = 100

                    lots = int(self.max_money_for_lot /
                               self.last_trade_price(ticker))
                    if rsi >= 70:
                        if self.balance(ticker)[1] >= 0:
                            self.order_set(ticker, 'sell', 'market', lots)
                    elif rsi <= 30:
                        if self.balance(ticker)[1] <= 0:
                            self.order_set(ticker, 'buy', 'market', lots)
