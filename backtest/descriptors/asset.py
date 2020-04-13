UNDEFINED = "undefined"


class Descriptor:
    label: str
    ticker: str
    asset_class: str
    product_type: str

    def __init__(self, ticker: str, label: str = None, asset_class: str = None, product_type: str = None) -> None:
        self.label, self.ticker, self.asset_class, self.product_type = label, ticker, asset_class, product_type

    def __repr__(self):
        return self.ticker

    def __str__(self):
        return self.ticker

    def __hash__(self) -> int:
        return "{}|{}".format(self.label, self.ticker).__hash__()

    def __lt__(self, other):
        return self.ticker < other.ticker

    def __eq__(self, other):
        return isinstance(other, Descriptor) and self.label == other.label and self.ticker == other.ticker
