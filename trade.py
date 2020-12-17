class Trade:
    def __init__(self,
                 buyer: str,
                 seller: str,
                 price: float,
                 lots: int):
        self.buyer = buyer
        self.seller = seller
        self.price = price
        self.lots = lots
