from orderbook import OrderBook
from accountant import Accountant
from dataprovider import DataProvider
from benchmarks import BuyAndHold, SellAndHold
from copy import deepcopy
from tqdm import tqdm


class MarketPlace:
    def __init__(self,
                 robots: ['Robot'],
                 ticker: str,
                 path_to_training_data: str = 'hist_prices.csv'):
        self.data_provider = DataProvider()
        self.robots = robots + [BuyAndHold(), SellAndHold()]
        self.accountant = Accountant(self.robots)
        self.order_book = OrderBook(ticker)
        self.path_to_training_data = path_to_training_data

    def training(self):
        training_data = self.data_provider.get_training_data(
            self.path_to_training_data)
        for robot in self.robots:
            robot.set_hist_prices(deepcopy(training_data))
            try:
                robot.train()
            except Exception as e:
                print(f'error while training in robot {robot.username}: {e}')

    def trading(self):
        orders = []
        data_from_order_book = self.order_book.get_data()
        robots_orders = self.order_book.get_robots_orders()
        for robot in self.robots:
            data_from_accountant = self.accountant.get_data(robot.username)
            robot.update(data_from_order_book,
                         robots_orders[robot.username] if robot.username in robots_orders else [],
                         data_from_accountant)
            try:
                robot.on_tick()
            except Exception as e:
                print(f'error while trading in robot {robot.username}: {e}')
            orders += robot.gather_new_orders()
        self.order_book.register_orders(orders)
        trades = self.order_book.get_last_trades()
        price = self.order_book.get_last_tick()
        self.accountant.register_trades(trades, price)

    def start(self,
              path: str):
        self.training()
        self.data_provider.prepare_for_trading(path)
        for orders in tqdm(self.data_provider):
            self.order_book.register_orders(orders)
            trades = self.order_book.get_last_trades()
            price = self.order_book.get_last_tick()
            self.accountant.register_trades(trades, price)
            self.trading()
        self.accountant.show_price_stats()
        self.accountant.print_robots_results()
        self.accountant.show_robot_stats()


if __name__ == '__main__':
    from lar import Lar

    robots = [
        Lar(1000),
        Lar(1000, 0.4, 0.4),
        Lar(1000, 0.6, 0.6),
        Lar(1500),
        Lar(1500, 0.4, 0.4),
        Lar(1500, 0.6, 0.6),
        Lar(500),
        Lar(500, 0.4, 0.4),
        Lar(500, 0.6, 0.6)
    ]

    m = MarketPlace(robots, 'SBER', 'hist_prices.csv')
    m.start('OrderLog20151211.txt')
