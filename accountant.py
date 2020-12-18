import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas as pd
import datetime as dt


class Accountant:
    def __init__(self,
                 robots: list):
        self.robots_accounts = {}
        self.robots_balance_changes = {}
        self.prices = []
        self.previous_last_price = None
        for robot in robots:
            self.robots_balance_changes[robot.username] = []
            self.robots_accounts[robot.username] = {'cnp_price': 0.0,
                                                    'cnp_lots': 0.0,
                                                    'balance': 100000}
        self.i = 0

    def register_trades(self,
                        trades: list,
                        last_price: float):
        if self.previous_last_price is None:
            self.previous_last_price = last_price
        self.accrue_robots_results(last_price)
        self.register_price(last_price)
        for trade in trades:
            if trade.buyer is not None:
                self.register_robots_buy(trade)
            if trade.seller is not None:
                self.register_robots_sell(trade)
        self.previous_last_price = last_price

    def register_robots_buy(self,
                            trade: 'Trade'):
        cnp_price = self.robots_accounts[trade.buyer]['cnp_price']
        cnp_lots = self.robots_accounts[trade.buyer]['cnp_lots']
        if cnp_lots == 0:
            self.robots_accounts[trade.buyer]['cnp_lots'] = trade.lots
            self.robots_accounts[trade.buyer]['cnp_price'] = trade.price
        elif cnp_lots < 0:
            if cnp_lots + trade.lots == 0:
                d = (trade.price - self.previous_last_price) * -trade.lots
                self.robots_accounts[trade.buyer]['balance'] += d
                self.robots_accounts[trade.buyer]['cnp_lots'] = 0
                self.robots_accounts[trade.buyer]['cnp_price'] = 0.0
            elif cnp_lots + trade.lots > 0:
                d = (trade.price - self.previous_last_price) * cnp_lots
                self.robots_accounts[trade.buyer]['balance'] += d
                self.robots_accounts[trade.buyer]['cnp_lots'] += trade.lots
                self.robots_accounts[trade.buyer]['cnp_price'] = trade.price
            elif cnp_lots + trade.lots < 0:
                d = (trade.price - self.previous_last_price) * -trade.lots
                self.robots_accounts[trade.buyer]['balance'] += d
                self.robots_accounts[trade.buyer]['cnp_lots'] += trade.lots
        elif cnp_lots > 0:
            self.robots_accounts[trade.buyer]['cnp_lots'] += trade.lots
            self.robots_accounts[trade.buyer]['cnp_price'] = self.calc_avco(
                cnp_price,
                cnp_lots,
                trade.price,
                trade.lots)

    def register_robots_sell(self,
                             trade: 'Trade'):
        cnp_price = self.robots_accounts[trade.seller]['cnp_price']
        cnp_lots = self.robots_accounts[trade.seller]['cnp_lots']
        if cnp_lots == 0:
            self.robots_accounts[trade.seller]['cnp_lots'] = -trade.lots
            self.robots_accounts[trade.seller]['cnp_price'] = trade.price
        elif cnp_lots > 0:
            if cnp_lots - trade.lots == 0:
                d = (trade.price - self.previous_last_price) * trade.lots
                self.robots_accounts[trade.seller]['balance'] += d
                self.robots_accounts[trade.seller]['cnp_lots'] = 0
                self.robots_accounts[trade.seller]['cnp_price'] = 0.0
            elif cnp_lots - trade.lots < 0:
                d = (trade.price - self.previous_last_price) * cnp_lots
                self.robots_accounts[trade.seller]['balance'] += d
                self.robots_accounts[trade.seller]['cnp_lots'] += trade.lots
                self.robots_accounts[trade.seller]['cnp_price'] = trade.price
            elif cnp_lots - trade.lots > 0:
                d = (trade.price - self.previous_last_price) * trade.lots
                self.robots_accounts[trade.seller]['balance'] += d
                self.robots_accounts[trade.seller]['cnp_lots'] -= trade.lots
        elif cnp_lots < 0:
            self.robots_accounts[trade.seller]['cnp_lots'] -= trade.lots
            self.robots_accounts[trade.seller]['cnp_price'] = self.calc_avco(
                cnp_price,
                cnp_lots,
                trade.price,
                -trade.lots
            )

    @staticmethod
    def calc_avco(cnp_price: float,
                  cnp_lots: int,
                  new_price: float,
                  new_lots: int):
        total_lots = cnp_lots + new_lots
        return abs((cnp_lots / total_lots) * cnp_price +
                   (new_lots / total_lots) * new_price)

    def accrue_robots_results(self,
                              last_price):
        delta = last_price - self.previous_last_price
        for robot in self.robots_accounts:
            cnp_lots = self.robots_accounts[robot]['cnp_lots']
            d = cnp_lots * delta
            self.robots_accounts[robot]['balance'] += d
            if self.i % 60 == 0:
                self.robots_balance_changes[robot].append(self.robots_accounts[robot]['balance'])
        self.i += 1

    def register_price(self,
                       last_price: float):
        self.prices.append(last_price)

    def get_data(self,
                 username: str):
        return self.robots_accounts[username]

    def show_robot_stats(self):
        df = pd.DataFrame(self.robots_balance_changes)
        df.index = pd.date_range(start=dt.datetime(2020, 12, 11, 10, 0, 0),
                                 periods=df.shape[0],
                                 freq=dt.timedelta(seconds=30))
        fig, ax = plt.subplots(figsize=(16, 9))
        fmt = dates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis_date()
        fig.autofmt_xdate()
        sns.lineplot(data=df)
        plt.xlabel('Торговая сессия')
        plt.ylabel('Счёт робота')
        plt.title('Динамика счёта робота')
        plt.show()

    def print_robots_results(self):
        balances = []
        for robot in self.robots_accounts:
            balances.append((robot, self.robots_accounts[robot]['balance']))
        balances.sort(key=lambda x: x[1], reverse=True)
        for balance in balances:
            print(f'{balance[0]} - {balance[1]:.2f}')

    def show_price_stats(self):
        fig, ax = plt.subplots(figsize=(16, 9))
        fmt = dates.DateFormatter('%H:%M:%S')
        ax.xaxis.set_major_formatter(fmt)
        ax.xaxis_date()
        fig.autofmt_xdate()
        sns.lineplot(x=pd.date_range(start=dt.datetime(2020, 12, 11, 10, 0, 0),
                                     periods=len(self.prices),
                                     freq=dt.timedelta(seconds=0.5)),
                     y=self.prices)
        plt.xlabel('Торговая сессия')
        plt.ylabel('Цена актива')
        plt.title('Динамика цены актива за один торговый день')
        plt.show()
