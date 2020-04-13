from backtest.descriptors.asset import Descriptor

IDX_ASSET_CLASS = "IDX"
ETF_ASSET_CLASS = "ETF"


class Idx(Descriptor):
    def __init__(self, ticker: str, label: str = None) -> None:
        super().__init__(ticker, label, IDX_ASSET_CLASS)


class Etf(Descriptor):
    def __init__(self, ticker: str, label: str = None) -> None:
        super().__init__(ticker, label, ETF_ASSET_CLASS)


SP500 = Idx("^GSPC", "S&P500 Index")
SPY = Etf("SPY", "SPDR S&P 500 ETF Trust")
