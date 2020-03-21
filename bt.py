import multiprocessing
import traceback
from concurrent.futures import Future
from multiprocessing import Lock
from typing import NamedTuple, Callable, Iterable
import concurrent.futures
import time
from datetime import datetime, timedelta
from typing import NamedTuple, Callable, Iterable

import matplotlib.pyplot as plt
import pandas as pd
from numpy.matlib import random

from codes.currencies import Ccy, AUD
from rates import RatesCollection, Strategy, InMemoryRatesCollection, Rate, Indicator

_ONE_YEAR = 365
_SUMMARY_START_DT_COLUMN = "start_dt"
_SUMMARY_PERCENTILE_COLUMN = "percentile"
_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN = "annualised_performance"
pd.set_option("display.precision", 8)


class PerformancePercentile:
    percentile: float
    annualised_performance: dict

    def __init__(self, percentile: float, annualised_performance: dict) -> None:
        self.percentile, self.annualised_performance = percentile, annualised_performance

    def get_df_row(self) -> dict:
        df_row = self.__dict__
        df_row.update(self.annualised_performance)
        return df_row


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
            print()
            print(self.df)

    def plot_dt_performance(self):
        min_y = self.df[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].min() * 0.95
        max_y = self.df[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].max() * 1.05
        self.df.plot(x=_SUMMARY_START_DT_COLUMN, y=_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN, ylim=(min_y, max_y))
        plt.show()

    def plot_percentile_performance(self):
        min_y = self.percentiles[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].min() * 0.9
        max_y = self.percentiles[_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN].max() * 1.1
        self.percentiles.plot(x=_SUMMARY_PERCENTILE_COLUMN, y=_SUMMARY_ANNUALISED_PERFORMANCE_COLUMN,
                              ylim=(min_y, max_y))
        plt.show()


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
        for percentile in range(0, 101):
            performance = df.quantile(percentile / float(100))
            row = PerformancePercentile(percentile=percentile, annualised_performance=performance).get_df_row()
            performance_df = performance_df.append(row, True)
        return Summary(df, performance_df)

    def run(self, worker_count=1) -> Summary:
        runs_by_run_id = dict()
        print("Starting simulations.")

        with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count) as pool:
            for dated_run_context in self._map_run_ids_to_rates():
                futures = []
                dt, run_ids, rc = dated_run_context.dt, dated_run_context.run_ids, dated_run_context.rc
                # pre compute std stats only once per date to make it overall more efficient
                # ...
                indicators = []
                print("Running simulation for date {}.".format(dt))
                for run_id in run_ids:
                    # if run_id not in lock_dict:
                    #     lock_dict[run_id] = m.Lock()
                    # lock = lock_dict[run_id]
                    # self._process_dt_for_run_id(current_run=current_run, dt=dt, rc=rc, indicators=indicators)

                    default_strategy = self.strategy_supplier(run_id=run_id, init_capital=1000, home_ccy=AUD)
                    default_run_data = RunData(run_id=run_id, strategy=default_strategy)
                    current_run: RunData = runs_by_run_id.get(run_id, default_run_data)
                    run_future: Future = pool.submit(self._process_dt_for_run_id, current_run, dt, rc, indicators)
                    futures.append((run_id, run_future))

                for run_id, run_future in futures:
                    exception = run_future.exception()
                    if exception:
                        raise exception
                    runs_by_run_id[run_id] = run_future.result()
        return self.summarise(runs_by_run_id)

    @staticmethod
    def _process_dt_for_run_id(current_run: RunData, dt: datetime, rc: RatesCollection,
                               indicators: [Indicator]):
        strat = current_run.strategy
        strat.next_datetime(dt)
        strat.last_seen_rc(rc)
        strat.next(indicators, rc)
        return current_run


def sample_growth_data():
    current_val = 100
    rates = []
    dt = datetime(2000, 1, 1)
    for i in range(0, int(_ONE_YEAR * 0.3)):
        rates.append(Rate(Ccy("sample1", "sample1"), AUD, dt, current_val))
        current_val += current_val * random.randint(-32, 40) / float(100)
        dt += timedelta(days=1)
    return rates


def run():
    rc = InMemoryRatesCollection.from_list(sample_growth_data())
    bt = Backtest(rc=rc, strategy_supplier=BuyAsapHoldStrategy, duration_days=int(_ONE_YEAR * 0.1))
    summary = bt.run(4)
    summary.print()
    summary.plot_dt_performance()
    summary.plot_percentile_performance()


class WorkerCountTimeSum(NamedTuple):
    worker_count: int
    time_sum: float


def optimisation_test(sample_size=1, min_workers=1, max_workers=4):
    rc = InMemoryRatesCollection.from_list(sample_growth_data())
    bt = Backtest(rc=rc, strategy_supplier=BuyAsapHoldStrategy, duration_days=int(_ONE_YEAR * 0.1))
    time_sums = dict()
    for sample_index in range(0, sample_size):
        for worker_count in range(min_workers, max_workers + 1):
            start = time.time()
            bt.run(worker_count)
            end = time.time()
            existing_time_sum = time_sums.get(worker_count, 0)
            time_sums[worker_count] = existing_time_sum + end - start

    recommended_workers = max_workers
    best_time = None
    for worker_count, time_sum in time_sums.items():
        avg_time = time_sum / sample_size
        print(f"Worker count <{worker_count}> Average duration <{avg_time}>")
        if best_time is None or avg_time < best_time:
            best_time = avg_time
            recommended_workers = worker_count
    print("Recommended number of workers:", recommended_workers)


def process_fn(v):
    cpu_intensive()
    print("v is {}".format(v))
    return v + 1


def cpu_intensive():
    for l in range(0, 1000):
        for i in range(0, 100):
            j = (i ** 2) ** (i / 2)


def test():
    resource = dict()
    for i in range(0, 100):
        resource[i] = i
    starttime = time.time()
    results = []
    print("Starting")
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
        for k in resource.keys():
            v = resource[k]
            print("Submitting ", v)
            future: Future = pool.submit(process_fn, v)
            results.append((k, future,))

        for key, future in results:
            exception = future.exception()
            if exception:
                raise exception
            resource[key] = future.result()
    print('That took {} seconds'.format(time.time() - starttime))
    print("results {} ".format(resource))
    print("f {} ".format(results))


if __name__ == "__main__":
    run()
    # optimisation_test(sample_size=1, min_workers=1, max_workers=8)
    # test()
