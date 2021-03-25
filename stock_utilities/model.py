import typing
import enum
import datetime


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
    bid: float
    open_interest: float
    currency: str
    last_price: float
    implied_volatility: float
    last_trade_date: datetime.datetime


class OptionChain(typing.NamedTuple):
    calls: typing.List[OptionChainDatum]
    puts: typing.List[OptionChainDatum]
