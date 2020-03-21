UNDEFINED = "undefined"


class AssetDescriptor:
    label: str
    code: str
    asset_class: str
    product_type: str

    def __init__(self, code: str, label: str, asset_class: str, product_type: str = None) -> None:
        self.label, self.code, self.asset_class, self.product_type = label, code, asset_class, product_type

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code

    def __hash__(self) -> int:
        return "{}|{}".format(self.label, self.code).__hash__()

    def __eq__(self, other):
        return isinstance(other, AssetDescriptor) and self.label == other.label and self.code == other.code
