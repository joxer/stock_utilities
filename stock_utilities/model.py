import typing
import enum
import datetime
import math
import numpy as np
import scipy.stats as scipy_stats
class OptionType(enum.Enum):
    UNDEFINED = 0
    CALL = 1
    PUT = 2


class StockHistoryDatum(typing.NamedTuple):
    time: int
    open_value: float
    close_value: float
    high: float
    low: float
    volume: float
    dividends: float
    stock_splits: float


class OptionChainDatum(typing.NamedTuple):
    type: OptionType
    strike: float
    current_stock_price: float
    bid: float
    open_interest: float
    currency: str
    last_price: float
    implied_volatility: float
    option_date: datetime.datetime
    last_trade_date: datetime.datetime

    def generate_delta(self, risk: float) -> float:
        expire = (self.option_date - datetime.datetime.now()).total_seconds()/(365*24*60.0)
        d1 = (
            np.log(self.current_stock_price / self.strike) + (risk + math.pow(self.implied_volatility,2) / 2) * expire
        ) / (self.implied_volatility * np.sqrt(expire))

        if self.type == OptionType.CALL:
            return scipy_stats.norm.cdf(d1)
        else:
            return scipy_stats.norm.cdf(-d1)  


class OptionChain(typing.NamedTuple):
    calls: typing.List[OptionChainDatum]
    puts: typing.List[OptionChainDatum]
