import random
from datetime import datetime, timedelta

from backtest.codes.currencies import AUD, Ccy
from backtest.rates import Rate

ONE_YEAR = 365


def sample_growth_data():
    current_val = 100
    rates = []
    dt = datetime(2000, 1, 1)
    for i in range(0, int(ONE_YEAR * 0.3)):
        rates.append(Rate(Ccy("sample1", "sample1"), AUD, dt, current_val))
        current_val += current_val * random.randint(-32, 40) / float(100)
        dt += timedelta(days=1)
    return rates
