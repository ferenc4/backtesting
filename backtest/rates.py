import math
from datetime import datetime
from enum import Enum
from operator import eq, attrgetter
from typing import Iterable, Any

import pandas as pd
from pandas import DataFrame

from backtest.codes.asset import AssetDescriptor
from backtest.codes.currencies import Ccy

RATE_FROM_NAME_COLUMN = 'from_name'
RATE_TO_NAME_COLUMN = 'to_name'
RATE_DATE_COLUMN = 'dt'
RATE_PRICE_COLUMN = 'price'
_POSITION_VOLUME_COLUMN = 'volume'


class Filter:
    def __init__(self, field_name: str, field_value: Any, op=eq) -> None:
        self.field_name, self.field_value, self.op = field_name, field_value, op

    def exec(self, df):
        return self.op(df[self.field_name], self.field_value)


def exec_filters(df: DataFrame, filters: Iterable):
    current_result = None
    for current_filter in filters:
        if current_result is None:
            current_result = current_filter.exec(df)
        else:
            current_result = current_result & current_filter.exec(df)
    return current_result


class Indicator:
    pass


class TimeLength(Enum):
    DAY = 0


class Rate:
    def __init__(self,
                 from_name: AssetDescriptor,
                 to_name: AssetDescriptor,
                 dt: datetime,
                 value: float = None) -> None:
        self.from_name, self.to_name, self.dt, self.price = from_name, to_name, dt, value

    def __str__(self) -> str:
        return "{}/{} {} {}".format(self.from_name, self.to_name, self.dt, self.price)

    def __repr__(self) -> str:
        return self.__str__()

    # @property
    # def name(self):
    #     return self.name
    #
    # @property
    # def date(self):
    #     return self.date
    #
    # @property
    # def value(self):
    #     return self.value


class RatesCollection:
    def insert(self, rate: Rate) -> None:
        raise NotImplementedError()

    def filter(self, *filters: Filter):
        raise NotImplementedError()

    def filter_dates(self, from_date=None, to_date=None):
        raise NotImplementedError()

    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def merge(self, other_rates_collection):
        raise NotImplementedError()

    def to_csv(self, file_path: str):
        raise NotImplementedError()

    def last_dt(self):
        raise NotImplementedError()

    def get(self, index=0):
        raise NotImplementedError()

    def dates(self):
        raise NotImplementedError()


class Position:
    def __init__(self, descriptor: AssetDescriptor, volume: float) -> None:
        self.descriptor = descriptor
        self.volume = volume

    def __str__(self) -> str:
        return self.__dict__.__str__()

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __add__(self, other):
        if isinstance(other, Position) and self.descriptor == other.descriptor:
            return Position(descriptor=self.descriptor, volume=self.volume + other.volume)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Position) and self.descriptor == other.descriptor:
            return Position(descriptor=self.descriptor, volume=self.volume - other.volume)
        return NotImplemented

    def with_volume(self, volume: float):
        return Position(descriptor=self.descriptor, volume=volume)

    def rc_reval(self, rc: RatesCollection, output_currency: Ccy, dt: datetime = None):
        # todo address: the rate might not be available today
        if dt is None:
            dt = rc.last_dt()
        dt_filter = Filter(RATE_DATE_COLUMN, dt)
        from_filter = Filter(RATE_FROM_NAME_COLUMN, self.descriptor)
        to_filter = Filter(RATE_TO_NAME_COLUMN, output_currency)
        price = rc.filter(dt_filter, from_filter, to_filter).get()[RATE_PRICE_COLUMN]
        return self.volume * price


def no_position(asset: AssetDescriptor) -> Position:
    return Position(asset, 0)


class InMemoryRatesCollection(RatesCollection):

    def __init__(self, init_df=None, is_sorted=False):
        self.df: pd.Dataframe = init_df
        if init_df is None:
            self.df = pd.DataFrame()
        self.is_sorted = is_sorted

    def __str__(self) -> str:
        return self.df.__str__()

    def __repr__(self) -> str:
        return self.df.__repr__()

    def _sort(self):
        if not self.is_sorted:
            self.df.sort_values(by=RATE_DATE_COLUMN, axis=0, ascending=True, inplace=False, kind='quicksort',
                                na_position='last')
            self.is_sorted = True

    def __iter__(self) -> Iterable:
        self._sort()
        grouped = self.df.groupby(by=RATE_DATE_COLUMN)
        for dt, rates_df in grouped:
            yield (dt, InMemoryRatesCollection(rates_df, self.is_sorted))

    def dates(self):
        self._sort()
        return self.df[RATE_DATE_COLUMN].unique()

    @staticmethod
    def from_list(rates_ary: [Rate] = None) -> RatesCollection:
        if rates_ary is None:
            rates_ary = []
        rc = InMemoryRatesCollection()
        for rate in rates_ary:
            rc.insert(rate)
        rc._sort()
        return rc

    @staticmethod
    def from_csv(file_path: str) -> RatesCollection:
        df = pd.read_csv(file_path)
        return InMemoryRatesCollection(df)

    def __len__(self):
        return self.df.__len__()

    def insert(self, rate: Rate):
        self.df = self.df.append(rate.__dict__, ignore_index=True)
        self.is_sorted = False

    def filter(self, *filters: Filter) -> RatesCollection:
        grouped_filters = exec_filters(self.df, filters)
        return InMemoryRatesCollection(self.df[grouped_filters], self.is_sorted)

    def filter_dates(self, from_date_inclusive: datetime = None, to_date_inclusive: datetime = None) -> RatesCollection:
        search_result = self.df
        if from_date_inclusive and to_date_inclusive:
            search_result = self.df[from_date_inclusive <= self.df[RATE_DATE_COLUMN] <= to_date_inclusive]
        if from_date_inclusive:
            search_result = self.df[from_date_inclusive <= self.df[RATE_DATE_COLUMN]]
        if to_date_inclusive:
            search_result = self.df[self.df[RATE_DATE_COLUMN] <= to_date_inclusive]
        return InMemoryRatesCollection(search_result, self.is_sorted)

    def last_dt(self) -> datetime:
        return self.df.loc[self.df[RATE_DATE_COLUMN].idxmax()][RATE_DATE_COLUMN]

    def merge(self, other_rates_collection) -> RatesCollection:
        return InMemoryRatesCollection(self.df.append(other_rates_collection.df))

    def to_csv(self, file_path: str):
        return self.df.to_csv(file_path)

    def get(self, index=0):
        return self.df.iloc[index]


def for_capital(rc: RatesCollection, to_buy: AssetDescriptor, ccy_amount: Position) -> Position:
    price = rc.filter(Filter(RATE_DATE_COLUMN, rc.last_dt()), Filter(RATE_FROM_NAME_COLUMN, to_buy),
                      Filter(RATE_TO_NAME_COLUMN, ccy_amount.descriptor)).get()[RATE_PRICE_COLUMN]
    return Position(descriptor=to_buy, volume=math.floor(ccy_amount.volume / price))


class Strategy:
    def __init__(self, run_id, name, init_capital, home_ccy: Ccy):
        self._init_capital = init_capital
        self._home_ccy = home_ccy
        self._pos = {home_ccy: Position(home_ccy, init_capital)}
        self.name = name
        self._last_seen_rc: RatesCollection = None
        self.start_dt = None
        self.end_dt = None
        self._last_calculated_pnl = None
        self.run_id = run_id
        self._picked: AssetDescriptor = None

    def __str__(self) -> str:
        return self.__dict__.__str__()

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def pick_anything(self, use_last_picked=True):
        rc = self._last_seen_rc
        if self._picked is not None and use_last_picked:
            return self._picked
        self._picked = rc.filter(Filter(RATE_DATE_COLUMN, rc.last_dt()),
                                 Filter(RATE_TO_NAME_COLUMN, self._home_ccy)).get()[RATE_FROM_NAME_COLUMN]
        return self._picked

    def next_datetime(self, dt: datetime):
        if self.start_dt is None or self.start_dt > dt:
            self.start_dt = dt
        if self.end_dt is None or self.end_dt < dt:
            self.end_dt = dt

    def last_seen_rc(self, rates_collection: RatesCollection):
        self._last_seen_rc = rates_collection
        self._last_calculated_pnl = None

    def next(self, indicators: [Indicator], rates_collection: RatesCollection):
        raise NotImplementedError()

    def reval_portfolio(self, rates_collection: RatesCollection = None, reval_ccy: Ccy = None):
        if rates_collection is None:
            rates_collection = self._last_seen_rc
        if reval_ccy is None:
            reval_ccy = self._home_ccy
        portfolio_value = 0
        for asset, position in self._pos.items():
            if asset == reval_ccy:
                portfolio_value = portfolio_value + position.volume
            else:
                portfolio_value = portfolio_value + position.rc_reval(rates_collection, self._home_ccy)
        return Position(descriptor=reval_ccy, volume=portfolio_value)

    def _pnl(self):
        if self._last_calculated_pnl is None:
            net_difference = self.reval_portfolio().volume - self._init_capital
            self._last_calculated_pnl = net_difference / float(self._init_capital)
        return self._last_calculated_pnl

    def _duration_days(self):
        return (self.end_dt - self.start_dt).days

    def annualised_pnl(self):
        pnl = self._pnl()
        sign = -1 if pnl < 0 else 1
        result = sign * ((1 + float(abs(pnl))) ** (365.0 / float(self._duration_days())))
        return result

    def _buy(self, position: Position):
        position_cost = position.rc_reval(self._last_seen_rc, self._home_ccy)
        self._buy_for_amount(position.descriptor, position_cost)

    def _buy_for_amount(self, asset: AssetDescriptor, cost: Position):
        rt: float = self._last_seen_rc.filter(Filter(RATE_FROM_NAME_COLUMN, asset),
                                              Filter(RATE_TO_NAME_COLUMN, cost.descriptor)).get()[RATE_PRICE_COLUMN]
        affordable_asset_position: Position = for_capital(self._last_seen_rc, asset,
                                                          min([cost, self._pos[self._home_ccy]],
                                                              key=attrgetter(_POSITION_VOLUME_COLUMN)))
        affordable_cost_volume: float = affordable_asset_position.volume * rt
        self._pos[self._home_ccy] -= Position(descriptor=cost.descriptor, volume=affordable_cost_volume)
        self._pos[asset] = self._pos.get(asset, affordable_asset_position)
