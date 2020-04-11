from datetime import datetime
from operator import attrgetter

from backtest.codes.asset import AssetDescriptor
from backtest.codes.currencies import Ccy
from backtest.position import Position, for_capital
from backtest.rates.constants import RATE_DATE_COLUMN, RATE_TO_NAME_COLUMN, RATE_FROM_NAME_COLUMN, YEAR_DAYS, \
    RATE_PRICE_COLUMN, POSITION_VOLUME_COLUMN
from backtest.rates.rates import RatesCollection, Filter, Indicator


class Strategy:
    def __init__(self, run_id, name, init_capital, home_ccy: Ccy):
        self._init_capital = init_capital
        self._home_ccy = home_ccy
        self._pos = {home_ccy: Position(home_ccy, init_capital)}
        self.name = name
        self._last_seen_rc: RatesCollection = None
        self.start_dt = None
        self.end_dt = None
        self._last_calculated_pnl = None
        self.run_id = run_id
        self._picked: AssetDescriptor = None
        self._portfolio_value = None

    def __str__(self) -> str:
        return self.__dict__.__str__()

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def pick_anything(self, use_last_picked=True):
        rc = self._last_seen_rc
        if self._picked is not None and use_last_picked:
            return self._picked
        self._picked = rc.filter(Filter(RATE_DATE_COLUMN, rc.last_dt()),
                                 Filter(RATE_TO_NAME_COLUMN, self._home_ccy)).get()[RATE_FROM_NAME_COLUMN]
        return self._picked

    def next_datetime(self, dt: datetime):
        if self.start_dt is None or self.start_dt > dt:
            self.start_dt = dt
        if self.end_dt is None or self.end_dt < dt:
            self.end_dt = dt

    def last_seen_rc(self, rates_collection: RatesCollection):
        self._last_seen_rc = rates_collection
        self._last_calculated_pnl = None
        self._portfolio_value = None

    def next(self, indicators: [Indicator], rates_collection: RatesCollection):
        raise NotImplementedError()

    def reval_portfolio(self, rates_collection: RatesCollection = None, reval_ccy: Ccy = None):
        if self._portfolio_value is None:
            if rates_collection is None:
                rates_collection = self._last_seen_rc
            if reval_ccy is None:
                reval_ccy = self._home_ccy
            portfolio_volume = 0
            for asset, position in self._pos.items():
                if asset == reval_ccy:
                    portfolio_volume = portfolio_volume + position.volume
                else:
                    portfolio_volume = portfolio_volume + position.rc_reval(rates_collection, self._home_ccy)
            self._portfolio_value = Position(descriptor=reval_ccy, volume=portfolio_volume)
        return self._portfolio_value

    def _pnl(self):
        if self._last_calculated_pnl is None:
            net_difference = self.reval_portfolio().volume - self._init_capital
            self._last_calculated_pnl = net_difference / float(self._init_capital)
        return self._last_calculated_pnl

    def _duration_days(self):
        return (self.end_dt - self.start_dt).days

    def annualised_pnl(self):
        pnl = self._pnl()
        sign = -1 if pnl < 0 else 1
        abs_pnl = float(abs(pnl))
        days = self._duration_days()
        power = (float(YEAR_DAYS) / float(days)) if days < YEAR_DAYS else float(days) / float(YEAR_DAYS)
        result = sign * ((1 + abs_pnl) ** power)
        return result

    def _buy(self, position: Position):
        position_cost = position.rc_reval(self._last_seen_rc, self._home_ccy)
        self._buy_for_amount(position.descriptor, position_cost)

    def _sell(self, position: Position):
        self._portfolio_value = None
        # todo

    def _sell_all(self, asset: AssetDescriptor):
        pass

    def _buy_for_amount(self, asset: AssetDescriptor, cost: Position):
        rt: float = self._last_seen_rc.filter(Filter(RATE_FROM_NAME_COLUMN, asset),
                                              Filter(RATE_TO_NAME_COLUMN, cost.descriptor)).get()[RATE_PRICE_COLUMN]
        affordable_asset_position: Position = for_capital(self._last_seen_rc, asset,
                                                          min([cost, self._pos[self._home_ccy]],
                                                              key=attrgetter(POSITION_VOLUME_COLUMN)))
        affordable_cost_volume: float = affordable_asset_position.volume * rt
        self._pos[self._home_ccy] -= Position(descriptor=cost.descriptor, volume=affordable_cost_volume)
        self._pos[asset] = self._pos.get(asset, affordable_asset_position)
        self._portfolio_value = None
