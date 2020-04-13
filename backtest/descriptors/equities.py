from backtest.descriptors.asset import Descriptor

EQUITY_ASSET_CLASS = "EQ"


class Equity(Descriptor):
    def __init__(self, ticker: str, label: str = None) -> None:
        super().__init__(ticker, label, EQUITY_ASSET_CLASS)


TESLA = Equity("TSLA")
APPLE = Equity("AAPL")
MICROSOFT = Equity("MSFT")
