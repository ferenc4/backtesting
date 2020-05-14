from datetime import datetime

import backtest.rates.plot_transforms as transforms
from backtest.backtest import Backtest, BuyAsapHoldStrategy
from backtest.collections_math import add, divide_by_number
from backtest.descriptors.equities import Equity
from backtest.descriptors.indexes import SP500
from backtest.plotting import CsvFilePlot, WindowPlot, Plottable
from backtest.rates.constants import YEAR_DAYS, RATE_PRICE_COLUMN
from backtest.rates.load import from_yahoo_finance_api
from backtest.rates.rates import RatesCollection


def run(worker_count=1, duration_days=2 * YEAR_DAYS):
    assets = {SP500, Equity("BRK-B", "Berkshire"), Equity("TECH", "Tech")}
    rc: RatesCollection = from_yahoo_finance_api(assets, datetime(1999, 3, 22), datetime.today())
    rc.to_csv("test")
    plot_apply(rc=rc, apply=transforms.cumulative_percentage_deriv, worker_count=worker_count)


def plot_apply(rc: RatesCollection, apply, worker_count=1):
    rc.fillna()
    plot = WindowPlot()
    assets = rc.get_assets()
    paths = []
    for asset, asset_df in assets:
        plottable: Plottable = transforms.rc_date_cumulative_deriv_rate_transform(asset.label, asset_df)
        plot.plot(plottable.x, plottable.y, plottable.label)
        paths.append(apply(asset_df[RATE_PRICE_COLUMN].values))
    plot.show()


def average(paths):
    running_y = None
    for path in paths:
        if running_y is None:
            running_y = path
        else:
            running_y = add(running_y, path)
    return divide_by_number(running_y, paths.__len__())


def backtest(rc, worker_count, duration_days):
    bt = Backtest(rc=rc, strategy_supplier=BuyAsapHoldStrategy, duration_days=duration_days)
    summary = bt.test(worker_count)
    summary.print()
    summary.plot_percentile_performance(CsvFilePlot())
