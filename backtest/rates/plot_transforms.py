from backtest.collections_math import derive_percentage, cumulative
from backtest.plotting import Plottable
from backtest.rates.constants import RATE_PRICE_COLUMN, RATE_DATE_COLUMN


def rc_date_cumulative_deriv_rate_transform(label, asset_df) -> Plottable:
    x = asset_df[RATE_DATE_COLUMN]
    rate_col = asset_df[RATE_PRICE_COLUMN].values
    y = cumulative_percentage_deriv(rate_col)
    label = f"{label}_DERIVED"
    return Plottable(x, y, label)


def cumulative_percentage_deriv(rates: []):
    max_ = max(rates)
    y = list(cumulative(derive_percentage(rates, max_)))
    return y


def rc_date_rate_transform(asset, asset_df) -> Plottable:
    return Plottable(asset_df[RATE_DATE_COLUMN], asset_df[RATE_PRICE_COLUMN], asset)
