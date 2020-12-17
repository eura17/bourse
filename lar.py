from robot import Robot
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd


class Lar(Robot):
    def __init__(self, size=1000, p_up=0.5, p_down=0.5):
        super().__init__(f'lar_{size}: p_up={p_up}, p_down={p_down}')
        # параметры функции
        self.size = size
        self.p_up = p_up
        self.p_down = p_down
        self.zero = 0

        # параметры, которые я собираюсь переиспользовать
        self.lags = None
        self.p_bull = None
        self.p_bear = None

        self.volume = 1000

    def train(self):
        self.df['returns'] = self.df['close'] - self.df['close'].shift(1)
        lag3 = self.df.iloc[1:, -1]
        lag3.index = pd.RangeIndex(start=1, stop=len(self.df.index))
        lag2 = self.df.iloc[2:, -1]
        lag2.index = pd.RangeIndex(start=1, stop=len(self.df.index) - 1)
        lag1 = self.df.iloc[3:, -1]
        lag1.index = pd.RangeIndex(start=1, stop=len(self.df.index) - 2)
        lag0 = self.df.iloc[4:, -1]
        lag0.index = pd.RangeIndex(start=1, stop=len(self.df.index) - 3)
        close = self.df.iloc[4:, 4]
        close.index = pd.RangeIndex(start=1, stop=len(self.df.index) - 3)
        self.lags = pd.DataFrame({'close': close,
                                  'lag0': lag0,
                                  'lag1': lag1,
                                  'lag2': lag2,
                                  'lag3': lag3})
        self.lags = self.lags.head(-3)
        self.lags['increase'] = np.where(self.lags['lag0'] > self.zero,
                                         True, False)
        self.lags['decrease'] = np.where(self.lags['lag0'] < -self.zero,
                                         True, False)

        end = self.lags.shape[0] - 1
        start = end - self.size
        X = self.lags.iloc[start:end, 2:5]
        y_inc = self.lags.iloc[start:end, -2]
        y_dec = self.lags.iloc[start:end, -1]
        to_predict = self.lags.iloc[[end], 2:5]

        logreg_inc = LogisticRegression(random_state=0, solver='lbfgs')
        logreg_inc.fit(X, y_inc)
        self.p_bull = logreg_inc.predict_proba(to_predict)[:, 1].tolist()[0]
        logreg_dec = LogisticRegression(random_state=0, solver='lbfgs')
        logreg_dec.fit(X, y_dec)
        self.p_bear = logreg_dec.predict_proba(to_predict)[:, 1].tolist()[0]

    def on_tick(self):
        time = self.get_last_quote_time()
        if time.second == 59:
            # добавляю цену закрытия и пересчитываю параметры
            close_price = self.get_last_quote()
            lag0 = close_price - self.lags.iloc[-1, 0]
            inc = lag0 > self.zero
            dec = lag0 < -self.zero
            lags123 = self.lags.iloc[-1, 1:4].tolist()
            to_add = self.lags.shape[0] + 1
            self.lags.loc[to_add] = [close_price, lag0, *lags123, inc, dec]

            # переобучаюсь
            end = self.lags.shape[0] - 1
            start = end - self.size
            X = self.lags.iloc[start:end, 2:5]
            y_inc = self.lags.iloc[start:end, -2]
            y_dec = self.lags.iloc[start:end, -1]
            to_predict = self.lags.iloc[[end], 2:5]
            if y_inc.nunique() > 1:
                logreg_inc = LogisticRegression(random_state=0, solver='lbfgs')
                logreg_inc.fit(X, y_inc)
                self.p_bull = logreg_inc.predict_proba(to_predict)[:, 1].tolist()[0]
            if y_dec.nunique() > 1:
                logreg_dec = LogisticRegression(random_state=0, solver='lbfgs')
                logreg_dec.fit(X, y_dec)
                self.p_bear = logreg_dec.predict_proba(to_predict)[:, 1].tolist()[0]

        if time.second == 0:
            if self.p_bull > self.p_up and self.p_bear <= self.p_down:
                self.order_send('buy', 'market', self.volume)
            elif self.p_bull <= self.p_up and self.p_bear > self.p_down:
                self.order_send('sell', 'market', self.volume)


if __name__ == '__main__':
    r = Lar()
    r.df = pd.read_csv('hist_prices.csv')
    r.train()
    r.on_tick()
