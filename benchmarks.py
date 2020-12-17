from robot import Robot


class BuyAndHold(Robot):
    def __init__(self):
        super().__init__('buy and hold')

    def train(self):
        pass

    def on_tick(self):
        time = self.get_last_quote_time()
        if time.hour == 10 and time.minute == 0 and time.second == 0:
            balance = self.get_current_balance()
            price = self.get_last_quote()
            self.order_send('buy', 'market', balance / price)


class SellAndHold(Robot):
    def __init__(self):
        super().__init__('sell and hold')

    def train(self):
        pass

    def on_tick(self):
        time = self.get_last_quote_time()
        if time.hour == 10 and time.minute == 0 and time.second == 0:
            balance = self.get_current_balance()
            price = self.get_last_quote()
            self.order_send('sell', 'market', balance / price)
