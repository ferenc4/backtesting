import math
from datetime import datetime

from backtest.descriptors.asset import Descriptor
from backtest.descriptors.currencies import Ccy
from backtest.rates.constants import RATE_DATE_COLUMN, RATE_PRICE_COLUMN, RATE_FROM_NAME_COLUMN, RATE_TO_NAME_COLUMN
from backtest.rates.rates import RatesCollection, Filter


class Position:
    def __init__(self, descriptor: Descriptor, volume: float) -> None:
        self.descriptor = descriptor
        self.volume = volume

    def __str__(self) -> str:
        return self.__dict__.__str__()

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __add__(self, other):
        if isinstance(other, Position) and self.descriptor == other.descriptor:
            return Position(descriptor=self.descriptor, volume=self.volume + other.volume)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Position) and self.descriptor == other.descriptor:
            return Position(descriptor=self.descriptor, volume=self.volume - other.volume)
        return NotImplemented

    def with_volume(self, volume: float):
        return Position(descriptor=self.descriptor, volume=volume)

    def rc_reval(self, rc: RatesCollection, output_currency: Ccy, dt: datetime = None):
        # todo address: the rate might not be available today
        if dt is None:
            dt = rc.last_dt()
        dt_filter = Filter(RATE_DATE_COLUMN, dt)
        from_filter = Filter(RATE_FROM_NAME_COLUMN, self.descriptor)
        to_filter = Filter(RATE_TO_NAME_COLUMN, output_currency)
        price = rc.filter(dt_filter, from_filter, to_filter).get()[RATE_PRICE_COLUMN]
        return self.volume * price


def no_position(asset: Descriptor) -> Position:
    return Position(asset, 0)


def for_capital(rc: RatesCollection, to_buy: Descriptor, ccy_amount: Position) -> Position:
    price = rc.filter(Filter(RATE_DATE_COLUMN, rc.last_dt()), Filter(RATE_FROM_NAME_COLUMN, to_buy),
                      Filter(RATE_TO_NAME_COLUMN, ccy_amount.descriptor)).get()[RATE_PRICE_COLUMN]
    return Position(descriptor=to_buy, volume=math.floor(ccy_amount.volume / price))
