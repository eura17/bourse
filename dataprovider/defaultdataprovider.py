from typing import NoReturn, Iterable
import datetime as dt

from dataprovider.dataprovider import DataProvider
from db.dataclasses import Order


class DefaultDataProvider(DataProvider):
    _dt_fmt = '%H%M%S%f'

    def __init__(self,
                 date_to_file: dict[dt.date, str],
                 tickers: Iterable[str]):
        super().__init__()
        self.date_to_file = date_to_file
        self.tickers = set(tickers)
        self.current_file = None
        self._extra_order = None

    def get_dates(self) -> list[dt.date]:
        return sorted(self.date_to_file)

    def get_tickers(self) -> set[str]:
        return self.tickers

    def prepare_to_load_orders_for_date(self, date: dt.datetime) -> NoReturn:
        self.current_file = open(self.date_to_file[date], 'r', encoding='utf8')
        self.current_file.readline()

    def get_trading_time_bounds(self, date: dt.date) -> tuple[dt.datetime,
                                                              dt.datetime]:
        with open(self.date_to_file[date], 'r', encoding='utf8') as f:
            f.readline()
            start_dt = dt.datetime.strptime(
                f.readline().split(',')[3],
                self._dt_fmt
            )
            for line in f:
                pass
            end_dt = dt.datetime.strptime(
                line.split(',')[3],
                self._dt_fmt
            )
        start_dt = dt.datetime(
            date.year,
            date.month,
            date.day,
            start_dt.hour,
            start_dt.minute,
            start_dt.second,
            start_dt.microsecond
        )
        end_dt = dt.datetime(
            date.year,
            date.month,
            date.day,
            end_dt.hour,
            end_dt.minute,
            end_dt.second,
            end_dt.microsecond
        )
        return start_dt, end_dt

    def get_orders(self,
                   start_dt: dt.datetime,
                   end_dt: dt.datetime) -> list[Order]:
        orders = []
        if self._extra_order is not None:
            orders.append(self._extra_order)
            self._extra_order = None
        for line in self.current_file:
            line = line.split(',')
            sec_code = line[1]
            if sec_code not in self.tickers:
                continue
            action = line[5]
            if action == '2':
                continue
            operation = line[2]
            datetime = dt.datetime.strptime(line[3], self._dt_fmt)
            datetime = dt.datetime(
                start_dt.year,
                start_dt.month,
                start_dt.day,
                datetime.hour,
                datetime.minute,
                datetime.second,
                datetime.microsecond
            )
            real_order_no = int(line[4])
            price = float(line[6])
            volume = int(line[7])
            order = Order(
                sec_code,
                'buy' if operation == 'B' else 'sell',
                'market' if price == 0 else 'limit',
                datetime,
                'set' if action == '1' else 'del',
                price,
                volume
            )
            order.set_real_order_no(real_order_no)
            if start_dt <= datetime < end_dt:
                orders.append(order)
            elif datetime >= end_dt:
                self._extra_order = order
                break
        return orders
