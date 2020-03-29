from datetime import datetime

import requests

from backtest.codes.currencies import AUD
from backtest.rates import RatesCollection, InMemoryRatesCollection, Rate

_FMP_DATE_FIELD_FORMAT = "%Y-%m-%d"
_FMP_VOLUME_FIELD_NAME = "volume"
_FMP_ADJ_CLOSE_PRICE_FIELD_NAME = "adjClose"
_FMP_DATE_FIELD_NAME = "date"
_FMP_LOAD_HISTORICAL_PRICES_ARRAY_FIELD_NAME = "historical"
_FMP_ENDPOINT_LOAD_HISTORICAL_PRICES = "https://financialmodelingprep.com/api/v3/historical-price-full/{}"


def from_fmp_api(*asset_symbols) -> RatesCollection:
    rc = InMemoryRatesCollection()
    for asset_symbol in asset_symbols:
        res: requests.Response = requests.get(_FMP_ENDPOINT_LOAD_HISTORICAL_PRICES.format(asset_symbol))
        json_ary = res.json()[_FMP_LOAD_HISTORICAL_PRICES_ARRAY_FIELD_NAME]
        for json_elem in json_ary:
            raw_date_field = json_elem[_FMP_DATE_FIELD_NAME]
            extracted_datetime = datetime.strptime(raw_date_field, _FMP_DATE_FIELD_FORMAT)
            rate = Rate(from_name=asset_symbol, to_name=AUD, dt=extracted_datetime,
                        value=json_elem[_FMP_ADJ_CLOSE_PRICE_FIELD_NAME], volume=json_elem[_FMP_VOLUME_FIELD_NAME])
            rc.insert(rate)
    return rc
