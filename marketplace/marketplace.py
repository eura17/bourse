from typing import Union, NoReturn
import datetime as dt
from copy import deepcopy

from dataprovider import DataProvider
from robot import Robot
from matchingengine import MatchingEngine
from broker import Broker


class MarketPlace:
    def __init__(self,
                 data_provider: DataProvider,
                 robots: list[Robot],
                 training_data=None,
                 accounts_settings: dict[str,
                                         dict[str,
                                              Union[int, float]]] = None,
                 discreteness: dt.timedelta = dt.timedelta(seconds=1),
                 save: bool = False):
        super().__init__()
        robot_names = set()
        for robot in robots:
            robot_names.add(robot.name)

        self.data_provider = data_provider
        self.dates = self.data_provider.get_dates()
        tickers = self.data_provider.get_tickers()

        self.order_book = MatchingEngine(
            tickers,
            robot_names
        )
        self.broker = Broker(
            robot_names,
            tickers,
            accounts_settings
        )

        self.robots = robots
        self.training_data = training_data
        self.discreteness = discreteness
        self.save = save

    def train_robots(self) -> NoReturn:
        for robot in self.robots:
            try:
                robot.training(deepcopy(self.training_data))
            except Exception as e:
                print(e)
        del self.training_data

    def trade(self,
              date: dt.date):
        self.order_book.create_order_log()
        self.order_book.create_trade_log()
        start_dt, end_dt = self.data_provider.get_trading_time_bounds(date)
        self.data_provider.prepare_to_load_orders_for_date(date)
        while start_dt < end_dt:
            orders = self.data_provider.get_orders(start_dt,
                                                   start_dt+self.discreteness)
            for order in orders:
                trades = self.order_book.process_order(order)
                for trade in trades:
                    self.broker.process_trade(trade)
            Robot.set_datetime(start_dt + self.discreteness)
            for robot in self.robots:
                #try:
                robot.trading()
                #except Exception as e:
                #    print(e)
                orders = robot.gather_orders()
                for order in orders:
                    if self.broker.validate_order(order):
                        trades = self.order_book.process_order(order)
                        for trade in trades:
                            self.broker.process_trade(trade)
                robot.reset_orders()
            start_dt += self.discreteness
        if self.save:
            self.order_book.save_order_log('')
            self.order_book.save_trade_log('')

    def start(self):
        self.train_robots()
        for date in self.dates:
            self.trade(date)
