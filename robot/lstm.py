import os

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

from robot.baserobot import BaseRobot


class LSTMRobot(BaseRobot):
    __DEFAULT_LOOKBACK_PERIOD = 30
    __DEFAULT_FORECAST_PERIOD = 22
    __DEFAULT_PERIODICITY = '1m'

    def __init__(self, options):
        super().__init__('LSTM')

        self.forecast_period = options.get('forecast_period',
                                           self.__DEFAULT_FORECAST_PERIOD)
        self.lookback_period = options.get('lookback_period',
                                           self.__DEFAULT_LOOKBACK_PERIOD)
        p = options.get('periodicity', self.__DEFAULT_PERIODICITY)
        if p in self.timeframes:
            self.periodicity = p
        else:
            self.periodicity = self.__DEFAULT_PERIODICITY

        self.data = None
        self.scaler = None
        self.regression = None

        self.max_money_for_lot = None

    def fit_lstm(self):
        X_train = self.data[:, [0, 1, 2, 4]]
        y_train = self.data[:, 3]
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

        n_s = len(self.data)
        n_i = len(self.data[0])
        n_o = 1
        a = 2
        n_h = int(n_s / (a * (n_i + n_o)))

        self.regression = Sequential()
        self.regression.add(LSTM(units=n_h,
                            activation='relu',
                            return_sequences=True,
                            input_shape=(X_train.shape[1], 1)))
        self.regression.add(Dropout(0.2))
        self.regression.add(LSTM(units=n_h,
                            activation='relu'))
        self.regression.add(Dropout(0.2))
        self.regression.add(Dense(units=1))
        self.regression.compile(optimizer='adam', loss='mse')

        self.regression.fit(X_train, y_train, epochs=10, batch_size=32)

    def training(self, training_data) -> None:
        self.max_money_for_lot = self.liquidation_cost() / len(self.tickers)

        self.data = []
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'candles.csv')) as f:
            f.readline()
            for line in f:
                self.data.append(
                    list(map(float, line.split(',')[2:]))
                )
        self.data = np.array(self.data)
        self.scaler = MinMaxScaler()

        self.data = self.scaler.fit_transform(self.data)
        self.fit_lstm()

    def trading(self) -> None:
        if self.datetime.second == 1:
            for ticker in self.tickers:
                candles = self.candles(ticker, self.periodicity, 2)
                if candles:
                    self.refit(candles[0])
                    if len(candles) == 2:
                        predict = self.predict(candles[-1])
                        lots = 2 * int(self.max_money_for_lot /
                                       self.last_trade_price(ticker))
                        if np.sign(predict[len(predict)-1] - predict[0]) == -1:
                            if self.balance(ticker)[1] >= 0:
                                self.order_set(ticker, 'sell', 'market', lots)
                        else:
                            if self.balance(ticker)[1] <= 0:
                                self.order_set(ticker, 'buy', 'market', lots)

    def refit(self, candle):
        new_info = np.array(
            [candle.open, candle.high, candle.low, candle.close, candle.volume]
        ).reshape((1, -1))
        scaled = self.scaler.transform(new_info)
        self.data = np.append(self.data, scaled)

    def predict(self, candle):
        pred = self.regression.predict(np.array(
            np.reshape([candle.open, candle.high, candle.low, candle.volume],
                       (1, 4, 1))
        ))
        pred *= 1 / self.scaler.scale_[0]
        return pred
