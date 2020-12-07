from orderbook import OrderBook
from accountant import Accountant
from dataprovider import DataProvider


class MarketPlace:
    def __init__(self,
                 robots: list,
                 ticker: str):
        self.data_provider = DataProvider()
        self.robots = robots
        self.accountant = Accountant(robots)
        self.order_book = OrderBook(ticker)

    def training(self,
                 data: 'pd.Dataframe'):
        for robot in self.robots:
            robot.train(data)

    def trading(self):
        actions = []
        for robot in self.robots:
            robot.update()
            robot.on_tick()
            actions += robot.gather_actions()
        trades = self.order_book.register_orders(actions)
        self.accountant.register_trades(trades)

    def start(self):
        training_data = self.data_provider.get_training_data()
        self.training(training_data)
        self.data_provider.prepare()
        for event in self.data_provider:
            self.order_book.update(event)
            self.trading()
        # output
