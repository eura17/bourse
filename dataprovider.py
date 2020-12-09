import os
import datetime as dt
import pandas as pd
from order import Order


class DataProvider:
    def __init__(self):
        self.path_to_training_data = ''
        self.path_to_trading_data = ''

        self.data = None
        self.last_second = 0
        self.extras = []

    def generate_training_data(self,
                               directory: str):
        tdt, tdo, tdh, tdl, tdc, tdv, tdd = [], [], [], [], [], [], []
        days = []
        files = os.listdir(directory)
        for file in files:
            days.append(self.extract_raw_candles_from_file(f'{directory}\\{file}'))
        for i in range(len(days)):
            t, o, h, l, c, v = self.process_candles(days[i])
            tdt += t
            tdo += o
            tdh += h
            tdl += l
            tdc += c
            tdv += v
            tdd += [i+1] * len(o)
        training_data = pd.DataFrame({'time': tdt,
                                      'open': tdo,
                                      'high': tdh,
                                      'low': tdl,
                                      'close': tdc,
                                      'volume': tdv,
                                      'day': tdd})
        self.path_to_training_data = 'hist_prices.csv'
        training_data.to_csv(self.path_to_training_data, index=False)

    @staticmethod
    def extract_raw_candles_from_file(path: str) -> [(dt.datetime, float, int)]:
        candles = []
        with open(path, 'r', encoding='utf-8') as f:
            f.readline()
            minute_candle, minute = [], 0
            for line in f:
                info = line.split(',')
                ticker, action = info[1], info[5]
                if ticker != 'SBER' or action != '2':
                    continue
                time = dt.datetime.strptime(info[3], '%H%M%S%f')
                if time.minute == minute:
                    minute_candle.append((time, float(info[9]), int(info[7])))
                else:
                    candles.append(minute_candle)
                    minute_candle, minute = [], time.minute
        return candles

    def process_candles(self,
                        candles: [(dt.datetime, float, int)]):
        t, o, h, l, c, v = [], [], [], [], [], []
        for candle in candles:
            t.append(candle[0][0].strftime('%H:%M:') + '00')
            o.append(candle[0][1])
            h.append(max(candle, key=lambda x: x[1])[1])
            l.append(min(candle, key=lambda x: x[1])[1])
            c.append(candle[-1][1])
            sv = 0
            for trade in candle:
                sv += trade[2]
            v.append(sv)
        return t, o, h, l, c, v

    def get_training_data(self,
                          path: str = None):
        path = path or self.path_to_training_data
        return pd.read_csv(path)

    def prepare_for_trading(self,
                            path):
        self.data = open(path, 'r', encoding='utf8')
        self.data.readline()

    def __iter__(self):
        return self

    def __next__(self):
        # вспоминаю не пробежал ли я лишний ордер
        orders = []
        while len(self.extras) != 0:
            orders += [self.extras.pop()]
        # бегу по файлику
        for line in self.data:
            info = line.split(',')
            ticker, action, price = info[1], info[5], float(info[6])
            time = dt.datetime.strptime(info[3], '%H%M%S%f')
            if ticker != 'SBER' or action != '1' or price == 0:
                if time.second != self.last_second:
                    self.last_second = time.second
                    return orders
                continue
            operation = 'buy' if info[2] == 'B' else 'sell'
            lots = int(info[7])
            to_delete = action == '0'
            order = Order(operation, 'limit', lots, price,
                          datetime=time, to_delete=to_delete)
            if time.second != self.last_second:
                orders.append(order)
            else:
                self.last_second = time.second
                self.extras.append(order)
        if len(orders) != 0:
            return orders
        else:
            self.data.close()
            raise StopIteration


if __name__ == '__main__':
    d = DataProvider()
    d.prepare_for_trading('OrderLog20151211.txt')
    start = dt.datetime.now()
    i = 0
    for elem in d:
        i += 1
        print(i)
    end = dt.datetime.now()
    print(end - start)
