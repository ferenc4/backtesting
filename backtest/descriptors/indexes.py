from backtest.descriptors.asset import Descriptor

IDX_ASSET_CLASS = "IDX"
ETF_ASSET_CLASS = "ETF"


class Idx(Descriptor):
    def __init__(self, ticker: str, label: str = None) -> None:
        super().__init__(ticker, label, IDX_ASSET_CLASS)


class Etf(Descriptor):
    def __init__(self, ticker: str, label: str = None) -> None:
        super().__init__(ticker, label, ETF_ASSET_CLASS)


SP500 = Idx("^GSPC", "S&P 500 Index")
ASX200 = Idx("^AXJO", "ASX 200 Index")
CAC40 = Idx("^FCHI", "CAC 40 Index")
CANADA_ETF = Idx("^GSPTSE", "S&P/TSX Comp. Index")
# not in yahoo finance
FTSE100 = Idx("^FTSE", "FTSE 100 Index")
NIKKEI225 = Idx("N225", "Nikkei 225 Index")

VWO = Etf("VWO")
SPY = Etf("SPY", "SPDR S&P 500 ETF Trust")
