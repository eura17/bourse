from orderbook import OrderBook
from accountant import Accountant
from dataprovider import DataProvider


class MarketPlace:
    def __init__(self,
                 robots: ['Robot'],
                 ticker: str):
        self.data_provider = DataProvider()
        self.robots = robots
        self.accountant = Accountant(robots)
        self.order_book = OrderBook(ticker)

    def training(self,
                 data: 'pd.DataFrame'):
        for robot in self.robots:
            robot.train(data)

    def trading(self):
        orders = []
        data_from_order_book = self.order_book.get_data()
        robots_orders = self.order_book.get_robots_orders()
        for robot in self.robots:
            data_from_accountant = self.accountant.get_data(robot.username)
            robot.update(data_from_order_book,
                         robots_orders[robot.username],
                         data_from_accountant)
            robot.on_tick()
            orders += robot.gather_new_orders()
        self.order_book.register_orders(orders)
        trades = self.order_book.get_last_trades()
        self.accountant.register_trades(trades)

    def start(self,
              path: str):
        #training_data = self.data_provider.get_training_data()
        #self.training(training_data)
        self.data_provider.prepare_for_trading(path)
        i = 0
        total_orders = 0
        for orders in self.data_provider:
            i += 1
            total_orders += len(orders)
            #try:
            self.order_book.register_orders(orders)
            print(i)
        print(self.order_book.total_deals)
        print(total_orders)
        # output


if __name__ == '__main__':
    import datetime as dt
    start = dt.datetime.now()
    m = MarketPlace([], 'SBER')
    m.start('OrderLog20151211.txt')
    end = dt.datetime.now()
    print(end - start)
