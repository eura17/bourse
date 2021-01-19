from typing import Union, NoReturn
import os

from db import User


class UserBroker(User):
    def __init__(self):
        super().__init__('broker', 'broker')

    def configure(self) -> NoReturn:
        path = f'{os.path.dirname(os.path.realpath(__file__))}\\lua'
        lua_files = os.listdir(path)
        for file in lua_files:
            with open(f'{path}\\{file}', 'r', encoding='utf8') as f:
                self._conn.eval(f.read().strip())

    def create_account(self, robot: str) -> NoReturn:
        self._conn.call(
            'create_account_space',
            (robot, )
        )

    def add_asset(self,
                  robot: str,
                  asset: str,
                  price: Union[int, float] = 0,
                  volume: int = 0):
        self._conn.call(
            'add_asset_to_account',
            (robot,
             asset,
             price,
             volume)
        )

    def get_asset(self,
                  robot: str,
                  asset: str) -> list[int, float]:
        return self._conn.call(
            'get_asset_from_account',
            (robot,
             asset)
        )[0]

    def get_all_assets(self, robot: str) -> dict[str,
                                                 tuple[int, float]]:
        return self._conn.call(
            'get_all_assets_from_account',
            (robot, )
        )[0]

    def change_asset(self,
                     robot: str,
                     asset: str,
                     price: Union[int, float],
                     volume: int) -> NoReturn:
        self._conn.call(
            'change_asset_in_account',
            (robot,
             asset,
             price,
             volume)
        )

    def liquidation_cost(self,
                         robot: str) -> Union[int, float]:
        return self._conn.call(
            'calculate_liquidation_cost',
            (robot, )
        )[0]

    def last_trade_price(self,
                         ticker: str) -> Union[int, float]:
        return self._conn.call(
            'get_last_trade_price',
            (ticker, )
        )[0]

    def min_ask_price(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'min_ask_price',
            (ticker,)
        )[0]

    def max_bid_price(self, ticker: str) -> Union[int, float]:
        return self._conn.call(
            'max_bid_price',
            (ticker, )
        )[0]
