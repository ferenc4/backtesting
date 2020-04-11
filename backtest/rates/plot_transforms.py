from backtest.collections_math import derive_percentage, cumulative
from backtest.plotting import Plottable
from backtest.rates.constants import RATE_PRICE_COLUMN, RATE_DATE_COLUMN


def date_cumulative_deriv_rate_transform(asset, asset_df) -> Plottable:
    x = asset_df[RATE_DATE_COLUMN]
    rate_col = asset_df[RATE_PRICE_COLUMN].values
    max_ = max(rate_col)
    y = list(cumulative(derive_percentage(rate_col, max_)))
    label = f"{asset}_DERIVED"
    return Plottable(x, y, label)


def date_rate_transform(asset, asset_df) -> Plottable:
    return Plottable(asset_df[RATE_DATE_COLUMN], asset_df[RATE_PRICE_COLUMN], asset)
