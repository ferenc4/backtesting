from backtest.codes.asset import AssetDescriptor

CCY_ASSET_CLASS = "FX"


class Ccy(AssetDescriptor):

    def __init__(self, code: str, label: str) -> None:
        super().__init__(code, label, CCY_ASSET_CLASS)


AUD = Ccy("AUD", "Australian Dollars")
USD = Ccy("USD", "American Dollars")
