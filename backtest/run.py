from datetime import datetime

import backtest.rates.plot_transforms as transforms
from backtest.backtest import Backtest, BuyAsapHoldStrategy
from backtest.collections_math import add, divide_by_number
from backtest.descriptors.asset import Descriptor
from backtest.descriptors.indexes import VWO, SPY
from backtest.plotting import CsvFilePlot, WindowPlot, Plottable
from backtest.rates.constants import YEAR_DAYS, RATE_PRICE_COLUMN
from backtest.rates.load import from_yahoo_finance_api
from backtest.rates.rates import RatesCollection


def run(worker_count=1, duration_days=2 * YEAR_DAYS):
    # compare_cumulative_percentage_growth([VWO, SPY])
    assets = {VWO, SPY}
    # rc: RatesCollection = from_yahoo_finance_api(assets, datetime(2005, 5, 1), datetime.today())
    # rc.fillna()
    # for dt, df_for_dt in rc.df().groupby(by=RATE_DATE_COLUMN):
    #     print(df_for_dt)
    compare_cumulative_percentage_growth(assets)


def compare_cumulative_percentage_growth(assets: [Descriptor]):
    rc: RatesCollection = from_yahoo_finance_api(assets, datetime(2000, 5, 1), datetime.today())
    rc.fillna()
    plot = WindowPlot()
    assets = rc.get_assets()
    paths = []
    x = None
    max_date = datetime(year=1700, month=1, day=1)
    min_date = datetime.today()
    max_ = 0
    for asset, asset_df in assets:
        length = len(asset_df)
        if length > max_:
            max_ = length
    for asset, asset_df in assets:
        plottable: Plottable = transforms.rc_date_cumulative_deriv_rate_transform(asset, asset_df)
        plot.plot(plottable.x, plottable.y, plottable.label)
        paths.append(transforms.cumulative_percentage_deriv(asset_df[RATE_PRICE_COLUMN].values))
        x = plottable.x
    y = list(average(paths))
    plot.plot(x, y, "custom")
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
