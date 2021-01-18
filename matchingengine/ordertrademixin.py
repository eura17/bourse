from typing import Iterable, NoReturn


class OrderTradeMixin:
    _TICKERS = set()
    _ROBOTS = set()

    @classmethod
    def set_tickers(cls, tickers: Iterable[str]) -> NoReturn:
        cls._TICKERS = set(tickers)

    @property
    def tickers(self):
        return self._TICKERS

    @classmethod
    def set_robots(cls, robots: Iterable[str]) -> NoReturn:
        cls._ROBOTS = set(robots)

    @property
    def robots(self):
        return self._ROBOTS
