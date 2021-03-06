import concurrent.futures
import concurrent.futures
from concurrent.futures import Future
from datetime import datetime
from typing import NamedTuple, Callable, Iterable

import pandas as pd

from backtest.descriptors.currencies import Ccy, AUD
from backtest.plotting import WindowPlot
from backtest.rates.rates import RatesCollection, Indicator
from backtest.strategy import Strategy

ANNUALISED_PERFORMANCE_COLUMN = "annualised_performance"
_SUMMARY_START_DT_COLUMN = "start_dt"
_SUMMARY_PERCENTILE_COLUMN = "percentile"
_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN = "annualised_performance"
pd.set_option("display.precision", 8)


class PerformancePercentile:
    percentile: int
    annualised_performance: float

    def __init__(self, percentile: int, annualised_performance: float) -> None:
        self.percentile, self.annualised_performance = percentile, annualised_performance


class RunData(NamedTuple):
    run_id: int
    strategy: Strategy


class DatedRunContext:
    dt: datetime
    run_ids: [int]
    rc: RatesCollection

    def __init__(self, dt: datetime, run_ids: [int], rc: RatesCollection) -> None:
        self.dt, self.run_ids, self.rc = dt, run_ids, rc


class BuyAsapHoldStrategy(Strategy):

    def __init__(self, run_id: str, init_capital, home_ccy: Ccy):
        super().__init__(run_id=run_id, name="BuyAsapHoldStrategy", home_ccy=home_ccy, init_capital=init_capital)

    def next(self, indicators: [Indicator], rates_collection: RatesCollection):
        self._buy_for_amount(self.pick_anything(), self._pos[self._home_ccy])


class Summary:
    def __init__(self, df: pd.DataFrame, percentiles: pd.DataFrame):
        self.df = df
        self.percentiles = percentiles

    def __str__(self) -> str:
        return self.df.__str__()

    def __repr__(self) -> str:
        return self.df.__repr__()

    def print(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'expand_frame_repr', False):
            print(self.df.describe(percentiles=[0.03, 0.25, 0.50, 0.75, 0.97]))
            print(self.percentiles)

    def plot_dt_performance(self, plot=None):
        if plot is None:
            plot = WindowPlot()
        plot.plot(x=self.df[_SUMMARY_START_DT_COLUMN].values,
                  y=self.df[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].values,
                  label=_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN,
                  do_show=True)

    def plot_percentile_performance(self, plot=None):
        if plot is None:
            plot = WindowPlot()
        plot.plot(x=self.percentiles[_SUMMARY_PERCENTILE_COLUMN].values,
                  y=self.percentiles[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].values,
                  label=_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN,
                  do_show=True)


class SummaryEntry(NamedTuple):
    strategy_name: str
    start_dt: datetime
    end_dt: datetime
    duration_days: int
    annualised_performance: float


class Backtest:
    def __init__(self, rc: RatesCollection, strategy_supplier: Callable, duration_days: int = 5 * 12 * 365):
        self.rc = rc
        self.duration_days = duration_days
        self.strategy_supplier = strategy_supplier

    # Actual list of time series with length 3:
    # 012
    # 123
    # 234
    # 345
    #
    # Distribution of rates for each run:
    # 0 [0]
    # 1 [0,1]
    # 2 [1,2]
    # 3 [2,3] # dont introduce runs with 0 length so no #4 run id
    def _generate_run_ids(self, origin, exclusive_upper_bound) -> Iterable:
        for i in range(0, self.duration_days):
            run_id = origin - i
            if 0 <= run_id < exclusive_upper_bound - 1:
                yield run_id

    def _map_run_ids_to_rates(self) -> Iterable:
        rates_count = len(self.rc.dates())
        # date won't be the same as run_id in the future
        origin = 0
        for dt, rc in self.rc:
            run_ids: [int] = list(self._generate_run_ids(origin, rates_count))
            origin += 1
            yield DatedRunContext(dt=dt, run_ids=run_ids, rc=rc)

    def summarise(self, runs_by_run_id: dict) -> Summary:
        print("Evaluating simulations.")
        df = pd.DataFrame()
        for _current_run in runs_by_run_id.values():
            current_run: RunData = _current_run
            strat: Strategy = current_run.strategy
            df = df.append(SummaryEntry(strategy_name=strat.name, start_dt=strat.start_dt, end_dt=strat.end_dt,
                                        duration_days=self.duration_days,
                                        annualised_performance=strat.annualised_pnl())._asdict(), True)
        performance_df = pd.DataFrame()
        df = df.sort_values(by=ANNUALISED_PERFORMANCE_COLUMN, axis=0, ascending=True, inplace=False,
                            kind='quicksort',
                            na_position='last')
        for percentile in range(0, min(101, len(df))):
            performance = df.iloc[percentile][_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN]
            row = PerformancePercentile(percentile=percentile, annualised_performance=performance).__dict__
            performance_df = performance_df.append(row, True)
        return Summary(df, performance_df)

    def execute_simulations(self, worker_count):
        runs_by_run_id = dict()
        print("Starting simulations.")
        with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count) as pool:
            for dated_run_context in self._map_run_ids_to_rates():
                futures = []
                dt, run_ids, rc = dated_run_context.dt, dated_run_context.run_ids, dated_run_context.rc

                # pre compute std stats only once per date to make it overall more efficient
                indicators = self.calc_indicators(dt)

                print("Running simulation for date {}.".format(dt))
                for run_id in run_ids:
                    default_strategy = self.strategy_supplier(run_id=run_id, init_capital=1000, home_ccy=AUD)
                    default_run_data = RunData(run_id=run_id, strategy=default_strategy)
                    current_run: RunData = runs_by_run_id.get(run_id, default_run_data)
                    run_future: Future = pool.submit(self._strategy_process_next, current_run, dt, rc, indicators)
                    futures.append((run_id, run_future))

                for run_id, run_future in futures:
                    exception = run_future.exception()
                    if exception:
                        raise exception
                    runs_by_run_id[run_id] = run_future.result()
        return runs_by_run_id

    def calc_indicators(self, current_date):
        # todo
        rc = self.rc
        return []

    def train(self, worker_count=1) -> None:
        return

    def test(self, worker_count=1) -> Summary:
        runs_by_run_id = self.execute_simulations(worker_count)
        return self.summarise(runs_by_run_id)

    @staticmethod
    def _strategy_process_next(current_run: RunData, dt: datetime, rc: RatesCollection,
                               indicators: [Indicator]):
        strat = current_run.strategy
        strat.next_datetime(dt)
        strat.last_seen_rc(rc)
        strat.next(indicators, rc)
        return current_run
