import random
from datetime import datetime, timedelta

from backtest.codes.currencies import AUD, Ccy
from backtest.rates import Rate

ONE_YEAR = 365


def sample_growth_data(days=ONE_YEAR):
    random.seed(1)
    ccy1_val = 100.0
    ccy2_val = 100.0
    rates = []
    dt = datetime(2000, 1, 1)
    ccy1 = Ccy("sample1", "")
    ccy2 = Ccy("sample2", "")
    for i in range(0, days):
        rates.append(Rate(ccy1, AUD, dt, ccy1_val))
        rates.append(Rate(ccy2, AUD, dt, ccy2_val))
        ccy1_val += ccy1_val * random.randint(-32, 40) / float(100)
        ccy2_val += ccy2_val * random.randint(-32, 40) / float(100)
        dt += timedelta(days=1)
    return rates
