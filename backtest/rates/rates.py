from datetime import datetime
from enum import Enum
from operator import eq
from typing import Iterable, Any

import pandas as pd
from pandas import DataFrame

from backtest.codes.asset import AssetDescriptor
from backtest.plotting import WindowPlot, Plot
from backtest.rates.constants import RATE_DATE_COLUMN, RATE_FROM_NAME_COLUMN
from backtest.rates.plot_transforms import date_rate_transform

pd.set_option("display.precision", 8)


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
                 value: float = None,
                 volume: float = None) -> None:
        self.from_name, self.to_name, self.dt, self.price, self.volume = from_name, to_name, dt, value, volume

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

    def df(self) -> DataFrame:
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

    def plot(self, transform_fn=None):
        raise NotImplementedError()


class InMemoryRatesCollection(RatesCollection):

    def __init__(self, init_df=None, is_sorted=False):
        self._df: pd.Dataframe = init_df
        if init_df is None:
            self._df = pd.DataFrame()
        self.is_sorted = is_sorted

    def __str__(self) -> str:
        return self._df.__str__()

    def __repr__(self) -> str:
        return self._df.__repr__()

    def _sort(self):
        if not self.is_sorted:
            self._df.sort_values(by=RATE_DATE_COLUMN, axis=0, ascending=True, inplace=False, kind='quicksort',
                                 na_position='last')
            self.is_sorted = True

    def __iter__(self) -> Iterable:
        self._sort()
        grouped = self._df.groupby(by=RATE_DATE_COLUMN)
        for dt, rates_df in grouped:
            yield (dt, InMemoryRatesCollection(rates_df, self.is_sorted))

    def dates(self):
        self._sort()
        return self._df[RATE_DATE_COLUMN].unique()

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
        return self._df.__len__()

    def insert(self, rate: Rate):
        self._df = self._df.append(rate.__dict__, ignore_index=True)
        self.is_sorted = False

    def filter(self, *filters: Filter) -> RatesCollection:
        grouped_filters = exec_filters(self._df, filters)
        return InMemoryRatesCollection(self._df[grouped_filters], self.is_sorted)

    def filter_dates(self, from_date_inclusive: datetime = None, to_date_inclusive: datetime = None) -> RatesCollection:
        search_result = self._df
        if from_date_inclusive is not None and to_date_inclusive is not None:
            ge_matches = from_date_inclusive <= self._df[RATE_DATE_COLUMN]
            le_matches = self._df[RATE_DATE_COLUMN] <= to_date_inclusive
            search_result = self._df[ge_matches & le_matches]
        if from_date_inclusive is not None:
            ge_matches = from_date_inclusive <= self._df[RATE_DATE_COLUMN]
            search_result = self._df[ge_matches]
        if to_date_inclusive is not None:
            le_matches = self._df[RATE_DATE_COLUMN] <= to_date_inclusive
            search_result = self._df[le_matches]
        return InMemoryRatesCollection(search_result, self.is_sorted)

    def last_dt(self) -> datetime:
        return self._df.loc[self._df[RATE_DATE_COLUMN].idxmax()][RATE_DATE_COLUMN]

    def merge(self, other_rates_collection: RatesCollection) -> RatesCollection:
        # for large csv files this will be more efficient with iterators rather than dataframes
        return InMemoryRatesCollection(self._df.append(other_rates_collection.df()))

    def to_csv(self, file_path: str):
        return self._df.to_csv(file_path)

    def get(self, index=0):
        return self._df.iloc[index]

    def plot(self, transform_fn=None, plot: Plot = None):
        if plot is None:
            plot = WindowPlot()
        if transform_fn is None:
            transform_fn = date_rate_transform
        assets = self._df.groupby(by=RATE_FROM_NAME_COLUMN)
        for asset, asset_df in assets:
            plottable = transform_fn(asset, asset_df)
            plot.plot(plottable.x, plottable.y, plottable.label)
        plot.show()

    def df(self) -> DataFrame:
        return self._df
