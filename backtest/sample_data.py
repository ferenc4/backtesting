import random
from datetime import datetime, timedelta

from backtest.descriptors.currencies import AUD, Ccy
from backtest.rates.rates import Rate

ONE_YEAR = 365

SAMPLE2 = Ccy("sample2", "")
SAMPLE1 = Ccy("sample1", "")


def sample_ccy_for(index: int):
    return Ccy(f"sample{index}", "")


def sample_growth_data(days=ONE_YEAR):
    random.seed(1)
    ccy1_val = 100.0
    ccy2_val = 100.0
    rates = []
    dt = datetime(2000, 1, 1)
    ccy1 = SAMPLE1
    ccy2 = SAMPLE2
    for i in range(0, days):
        rates.append(Rate(ccy1, AUD, dt, ccy1_val))
        rates.append(Rate(ccy2, AUD, dt, ccy2_val))
        ccy1_val += ccy1_val * random.randint(-32, 40) / float(100)
        ccy2_val += ccy2_val * random.randint(-32, 40) / float(100)
        dt += timedelta(days=1)
    return rates


def sample_data_from_array(price_paths: [[int]]):
    rates = []
    ccy_id = 1
    for price_path in price_paths:
        dt = datetime(2000, 1, 1)
        ccy1 = sample_ccy_for(ccy_id)
        for price in price_path:
            rates.append(Rate(ccy1, AUD, dt, price))
            dt += timedelta(days=1)
        ccy_id += 1
    return rates
