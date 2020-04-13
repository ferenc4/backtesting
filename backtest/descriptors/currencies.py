from backtest.descriptors.asset import Descriptor

CCY_ASSET_CLASS = "FX"


class Ccy(Descriptor):
    def __init__(self, ticker: str, label: str) -> None:
        super().__init__(ticker, label, CCY_ASSET_CLASS)


AUD = Ccy("AUD", "Australian Dollars")
USD = Ccy("USD", "American Dollars")
