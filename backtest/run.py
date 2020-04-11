from datetime import datetime

import backtest.rates.plot_transforms as transforms
from backtest.backtest import Backtest, BuyAsapHoldStrategy
from backtest.codes.equities import APPLE
from backtest.rates.constants import YEAR_DAYS
from backtest.rates.load import from_fmp_api
from backtest.rates.rates import RatesCollection


def run(worker_count=1, duration_days=2 * YEAR_DAYS):
    rc: RatesCollection = from_fmp_api(APPLE)
    rc = rc.filter_dates(datetime(2020, 2, 1))
    rc.plot(transforms.date_cumulative_deriv_rate_transform)
    bt = Backtest(rc=rc, strategy_supplier=BuyAsapHoldStrategy, duration_days=duration_days)
    summary = bt.test(worker_count)
    summary.print()
    summary.plot_percentile_performance()
