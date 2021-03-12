from hurst import compute_Hc

from robot.baserobot import BaseRobot


class HurstRobot(BaseRobot):
    def __init__(self, *args, **kwargs):
        super().__init__('Hurst')
        self.ma_period = 24
        self.hurst_period = 100
        self.hurst_bar = 0.5

        self.periodicity = '1m'

        self.max_money_for_lot = None

    def training(self, training_data) -> None:
        self.max_money_for_lot = self.liquidation_cost() / len(self.tickers)

    def trading(self) -> None:
        if self.datetime.second == 1:
            for ticker in self.tickers:
                candles = self.candles(ticker, self.periodicity,
                                       self.hurst_period)
                if len(candles) >= self.hurst_period:
                    closes = [candle.close for candle in candles]
                    hurst, c, data = compute_Hc(closes, simplified=False)
                    mean = 0
                    for close in closes[-self.ma_period:]:
                        mean += close / self.ma_period
                    price = self.last_trade_price(ticker)

                    lots = int(self.max_money_for_lot /
                               self.last_trade_price(ticker))
                    if hurst >= self.hurst_bar:
                        if price > mean:
                            if self.balance(ticker)[1] <= 0:
                                self.order_set(ticker, 'buy', 'market', lots)
                        elif price < mean:
                            if self.balance(ticker)[1] >= 0:
                                self.order_set(ticker, 'sell', 'market', lots)
                    else:
                        if price < mean:
                            if self.balance(ticker)[1] <= 0:
                                self.order_set(ticker, 'buy', 'market', lots)
                        elif price > mean:
                            if self.balance(ticker)[1] >= 0:
                                self.order_set(ticker, 'sell', 'market', lots)
