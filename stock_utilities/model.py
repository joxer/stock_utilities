import datetime
import enum
import math
import typing

import numpy as np
import scipy.stats as scipy_stats

import py_vollib.ref_python.black.greeks.analytical as vollib_a

from . import exceptions


class OptionType(enum.Enum):
    UNDEFINED = 0
    CALL = 1
    PUT = 2


class StockHistoryDatum(typing.NamedTuple):
    time: int
    symbol: str
    open_value: float
    close_value: float
    high: float
    low: float
    volume: float
    dividends: float
    stock_splits: float


class StockInformation(typing.NamedTuple):
    time: int
    symbol: str
    logo_url: str
    long_name: str
    average_volume_10_days: float
    average_volume: float
    market_cap: float
    float_shares: float
    implied_shares_outstanding: float
    short_ratio: float
    short_percent_float: float
    shares_short: float
    shares_short_previous_month_date: float
    shares_short_prior_month: float
    shares_percent_shares_out: float
    shares_outstanding: float
    shares_help_percent_insiders: float
    shares_hel_percent_institution: float


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

    def delta(self, risk: float = 0.0) -> float:
        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.option_date - datetime.datetime.now()).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.type == OptionType.CALL:
            return vollib_a.delta(
                "c",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )
        else:
            return vollib_a.delta(
                "p",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )

    def gamma(self, risk: float = 0) -> float:
        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.option_date - datetime.datetime.now()).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.type == OptionType.CALL:
            return vollib_a.gamma(
                "c",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )
        else:
            return vollib_a.gamma(
                "p",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )

    def tetha(self, risk: float = 0) -> float:
        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.option_date - datetime.datetime.now()).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.type == OptionType.CALL:
            return vollib_a.tetha(
                "c",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )
        else:
            return vollib_a.tetha(
                "p",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )

    def rho(self, risk: float = 0) -> float:
        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.option_date - datetime.datetime.now()).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.type == OptionType.CALL:
            return vollib_a.rho(
                "c",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )
        else:
            return vollib_a.rho(
                "p",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )

    def vega(self, risk: float = 0) -> float:
        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()
        expire = (self.option_date - datetime.datetime.now()).total_seconds() / (
            365 * 24 * 60.0
        )

        if self.type == OptionType.CALL:
            return vollib_a.vega(
                "c",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )
        else:
            return vollib_a.vega(
                "p",
                self.current_stock_price,
                self.strike,
                expire,
                risk,
                self.implied_volatility,
            )

    def payoff(self, contract_size: int = 100, position: int = 1) -> float:
        # negative position means short

        if self.type == OptionType.UNDEFINED:
            raise exceptions.OptionTypeIsUndefined()

        if self.type == OptionType.CALL:
            if position > 0:
                return (
                    (max(0, self.current_stock_price - self.strike) - self.last_price)
                    * contract_size
                    * position
                )
            else:
                return (
                    (self.last_price - max(0, self.current_stock_price - self.strike))
                    * contract_size
                    * position
                )
        else:
            if position > 0:
                return (
                    (max(0, self.strike - self.current_stock_price) - self.last_price)
                    * contract_size
                    * position
                )
            else:
                return (
                    (self.last_price - max(0, self.strike - self.current_stock_price))
                    * contract_size
                    * position
                )


class OptionChain(typing.NamedTuple):
    calls: typing.List[OptionChainDatum]
    puts: typing.List[OptionChainDatum]
