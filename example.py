from lar import Lar
from marketplace import MarketPlace

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

market_place = MarketPlace(robots, 'SBER', 'hist_prices.csv')
market_place.start('OrderLog20151211.txt')
