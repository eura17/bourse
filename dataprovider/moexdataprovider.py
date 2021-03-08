from typing import Iterable, Dict, List, Union
import datetime as dt

from dataprovider.basedataprovider import BaseDataProvider
from db.dataclasses import Order


class MOEXDataProvider(BaseDataProvider):
    def __init__(self,
                 date_to_file: Dict[dt.date, str],
                 tickers: Iterable[str],
                 discreteness: dt.timedelta = dt.timedelta(seconds=1)):
        super().__init__(tickers, discreteness)
        self.__date_to_file = date_to_file
        self.__current_file = None
        self.__current_date = None
        self.__extra_order = None

    def __open_next_file(self) -> bool:
        if self.__current_file is not None:
            self.__current_file.close()
        if len(self.__date_to_file) == 0:
            return False
        earliest_date = sorted(self.__date_to_file)[0]
        file = self.__date_to_file[earliest_date]
        self.__current_file = open(file, 'r', encoding='utf8')
        self.__current_file.readline()
        self.__current_date = earliest_date
        self.datetime = None
        del self.__date_to_file[earliest_date]
        return True

    def next_orders(self) -> Union[List[Order], None]:
        if self.__current_file is None:
            if not self.__open_next_file():
                return None
        orders = []
        if self.__extra_order is not None:
            orders.append(self.__extra_order)
            self.__extra_order = None
        for line in self.__current_file:
            line = line.split(',')
            order_datetime = dt.datetime.strptime(line[3], '%H%M%S%f')
            order_datetime = order_datetime.replace(
                year=self.__current_date.year,
                month=self.__current_date.month,
                day=self.__current_date.day
            )
            if self.datetime is None:
                self.datetime = order_datetime
            order_action = line[5]
            if order_action == '2':
                if order_datetime >= self.datetime + self.discreteness:
                    return orders
                continue
            order_sec_code = line[1]
            if order_sec_code not in self.tickers:
                if order_datetime >= self.datetime + self.discreteness:
                    return orders
                continue
            order_operation = line[2]
            order_real_order_no = int(line[4])
            order_price = float(line[6])
            order_volume = int(line[7])
            order = Order(
                order_sec_code,
                'buy' if order_operation == 'B' else 'sell',
                'market' if order_price == 0 else 'limit',
                order_datetime,
                'set' if order_action == '1' else 'del',
                order_price,
                order_volume
            )
            order.set_real_order_no(order_real_order_no)
            if self.datetime <= order_datetime < \
                    self.datetime + self.discreteness:
                orders.append(order)
            elif order_datetime >= self.datetime + self.discreteness:
                self.__extra_order = order
                return orders
        if len(orders) == 0:
            if not self.__open_next_file():
                return None
            else:
                return self.next_orders()
        return orders

