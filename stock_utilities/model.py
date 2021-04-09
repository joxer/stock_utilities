import dataclasses
import datetime
import enum
import math
import typing
import pytz

import numpy as np
import scipy.stats as scipy_stats

import py_vollib.black_scholes.greeks.analytical as vollib_a

from . import exceptions


class OptionType(enum.Enum):
    UNDEFINED = 0
    CALL = 1
    PUT = 2


class CorrelationHistoryDatum(typing.NamedTuple):
    time: datetime.datetime
    value: float


class StockHistoryDatum(typing.NamedTuple):
    time: datetime.datetime
    symbol: str
    currency: str
    open_value: float
    close_value: float
    high: float
    low: float
    volume: float
    dividends: float
    stock_splits: float


@dataclasses.dataclass
class StockInformation:
    time: int
    symbol: typing.Optional[str] = None
    logo_url: typing.Optional[str] = None
    long_name: typing.Optional[str] = None
    average_volume_10_days: typing.Optional[float] = None
    average_volume: typing.Optional[float] = None
    market_cap: typing.Optional[float] = None
    float_shares: typing.Optional[float] = None
    short_ratio: typing.Optional[float] = None
    short_percent_float: typing.Optional[float] = None
    shares_short: typing.Optional[float] = None
    shares_short_previous_month_date: typing.Optional[float] = None
    shares_short_prior_month: typing.Optional[float] = None
    shares_percent_shares_out: typing.Optional[float] = None
    shares_outstanding: typing.Optional[float] = None
    shares_implied_outstanding: typing.Optional[float] = None
    shares_held_percent_insiders: typing.Optional[float] = None
    shares_held_percent_institution: typing.Optional[float] = None

class OptionGreeks():

    def delta(self, risk: float = 0.0) -> float:
        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.get_option_date() - datetime.datetime.now(tz=pytz.timezone("UTC"))).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.get_type() == OptionType.CALL:
            return vollib_a.delta(
                "c",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )
        else:
            return vollib_a.delta(
                "p",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )

    def gamma(self, risk: float = 0) -> float:
        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.get_option_date() - datetime.datetime.now(tz=pytz.timezone("UTC"))).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.get_type() == OptionType.CALL:
            return vollib_a.gamma(
                "c",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )
        else:
            return vollib_a.gamma(
                "p",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )

    def theta(self, risk: float = 0) -> float:
        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.get_option_date() - datetime.datetime.now(tz=pytz.timezone("UTC"))).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.get_type() == OptionType.CALL:
            return vollib_a.theta(
                "c",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )
        else:
            return vollib_a.theta(
                "p",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )

    def rho(self, risk: float = 0) -> float:
        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.get_option_date() - datetime.datetime.now(tz=pytz.timezone("UTC"))).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.get_type() == OptionType.CALL:
            return vollib_a.rho(
                "c",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )
        else:
            return vollib_a.rho(
                "p",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )

    def vega(self, risk: float = 0) -> float:
        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.get_option_date() - datetime.datetime.now(tz=pytz.timezone("UTC"))).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.get_type() == OptionType.CALL:
            return vollib_a.vega(
                "c",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )
        else:
            return vollib_a.vega(
                "p",
                self.get_current_stock_price(),
                self.get_strike(),
                expire,
                risk,
                self.get_implied_volatility(),
            )

    def payoff(self, contract_size: int = 100, position: int = 1) -> float:
        # negative position means short

        if self.get_type() == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()

        if self.get_type() == OptionType.CALL:
            if position > 0:
                return (
                    (max(0, self.get_current_stock_price() - self.get_strike()) - self.get_last_price())
                    * contract_size
                    * position
                )
            else:
                return (
                    (self.get_last_price() - max(0, self.get_current_stock_price() - self.get_strike()))
                    * contract_size
                    * position
                )
        else:
            if position > 0:
                return (
                    (max(0, self.get_strike() - self.get_current_stock_price()) - self.get_last_price())
                    * contract_size
                    * position
                )
            else:
                return (
                    (self.get_last_price() - max(0, self.get_strike() - self.get_current_stock_price()))
                    * contract_size
                    * position
                )
@dataclasses.dataclass
class OptionChainDatum(OptionGreeks):
    option_type: OptionType
    option_symbol: str
    strike: float
    current_stock_price: float
    bid: float
    open_interest: float
    currency: str
    last_price: float
    implied_volatility: float
    option_date: datetime.datetime
    last_trade_date: datetime.datetime
    volume: float

    def get_last_price(self) -> float:
        return self.last_price
    def get_strike(self) -> float:
        return self.strike
    def get_current_stock_price(self) -> float:
        return self.current_stock_price
    def get_type(self) -> OptionType:
        return self.option_type
    def get_implied_volatility(self) -> float:
        return self.implied_volatility
    def get_option_date(self) -> datetime.datetime:
        return self.option_date


class OptionChain(typing.NamedTuple):
    calls: typing.List[OptionChainDatum]
    puts: typing.List[OptionChainDatum]
