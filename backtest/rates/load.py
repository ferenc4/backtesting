from datetime import datetime

import requests
from pandas_datareader.data import get_data_yahoo

from backtest.descriptors.asset import Descriptor
from backtest.descriptors.currencies import AUD
from backtest.rates.rates import RatesCollection, InMemoryRatesCollection, Rate

_FMP_DATE_FIELD_FORMAT = "%Y-%m-%d"
_FMP_VOLUME_FIELD_NAME = "volume"
_FMP_ADJ_CLOSE_PRICE_FIELD_NAME = "adjClose"
_FMP_DATE_FIELD_NAME = "date"
_FMP_LOAD_HISTORICAL_PRICES_ARRAY_FIELD_NAME = "historical"
_FMP_ENDPOINT_LOAD_HISTORICAL_PRICES = "https://financialmodelingprep.com/api/v3/historical-price-full/{}?apikey=demo"
_YAHOO_FINANCE_ADJ_CLOSE_PRICE_FIELD_NAME = "Adj Close"
_YAHOO_FINANCE_VOLUME_FIELD_NAME = "Volume"
_YAHOO_FINANCE_DATE_FIELD_FORMAT = "%d/%m/%Y"


def from_fmp_api(*tickers: Descriptor) -> RatesCollection:
    rc = InMemoryRatesCollection()
    for ticker in tickers:
        res: requests.Response = requests.get(_FMP_ENDPOINT_LOAD_HISTORICAL_PRICES.format(ticker))
        json_ary = res.json()[_FMP_LOAD_HISTORICAL_PRICES_ARRAY_FIELD_NAME]
        for json_elem in json_ary:
            rate = _rate_from_fmp_item(json_elem, ticker)
            rc.insert(rate)
    return rc


def _rate_from_fmp_item(json_elem, ticker):
    raw_date_field = json_elem[_FMP_DATE_FIELD_NAME]
    extracted_datetime = datetime.strptime(raw_date_field, _FMP_DATE_FIELD_FORMAT)
    rate = Rate(from_name=AUD, to_name=ticker, dt=extracted_datetime,
                value=json_elem[_FMP_ADJ_CLOSE_PRICE_FIELD_NAME], volume=json_elem[_FMP_VOLUME_FIELD_NAME])
    return rate


def from_yahoo_finance_api(tickers: [Descriptor], from_date: datetime = None,
                           to_date: datetime = None) -> RatesCollection:
    if from_date is not None:
        from_date = from_date.strftime(_YAHOO_FINANCE_DATE_FIELD_FORMAT)
    if to_date is not None:
        to_date = to_date.strftime(_YAHOO_FINANCE_DATE_FIELD_FORMAT)
    rc = InMemoryRatesCollection()
    for ticker in tickers:
        response = get_data_yahoo(ticker.ticker, from_date, to_date)
        for pandas_ts, row in response.iterrows():
            extracted_datetime = datetime(pandas_ts.year, pandas_ts.month, pandas_ts.day)
            rate = Rate(from_name=AUD, to_name=ticker, dt=extracted_datetime,
                        value=row[_YAHOO_FINANCE_ADJ_CLOSE_PRICE_FIELD_NAME],
                        volume=row[_YAHOO_FINANCE_VOLUME_FIELD_NAME])
            rc.insert(rate)

    return rc
