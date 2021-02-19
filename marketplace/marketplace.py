from typing import Iterable
from copy import deepcopy
from contextlib import suppress

from dataprovider import BaseDataProvider
from robot import BaseRobot
from matchingengine import BaseMatchingEngine
from broker import BaseBroker


class MarketPlace:
    def __init__(self,
                 data_provider: BaseDataProvider,
                 matching_engine: BaseMatchingEngine,
                 broker: BaseBroker,
                 robots: Iterable[BaseRobot],
                 training_data=None,
                 save_path: str = None):
        self.__data_provider = data_provider
        self.__matching_engine = matching_engine
        self.__broker = broker

        self.__robots = robots
        self.__training_data = training_data

        self.__save_path = save_path

        self.__suppress = suppress(BaseException)

    def train_robots(self) -> None:
        for robot in self.__robots:
            with self.__suppress:
                robot.training(deepcopy(self.__training_data))
        del self.__training_data

    def trade(self) -> None:
        for orders in self.__data_provider:
            for order in orders:
                trades = self.__matching_engine.process_order(order)
                for trade in trades:
                    self.__broker.process_trade(trade)
            BaseRobot.set_datetime(self.__data_provider.datetime)
            for robot in self.__robots:
                self.__broker.update_equity_curve(
                    self.__data_provider.datetime.timestamp(),
                    robot.name
                )
                with self.__suppress:
                    robot.trading()
                for order in robot.orders:
                    if self.__broker.validate_order(order):
                        trades = self.__matching_engine.process_order(order)
                        for trade in trades:
                            self.__broker.process_trade(trade)
                robot.reset()

    def start(self) -> None:
        self.__matching_engine.create_tables()

        self.train_robots()
        self.trade()

        if self.__save_path:
            self.__matching_engine.save_tables(self.__save_path)
            self.__broker.save_equity_curves(self.__save_path)
