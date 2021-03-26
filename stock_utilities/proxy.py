import abc
import datetime
import typing

import praw

import yfinance

from . import model


class DataProxy:
    def __init__(self, symbol: str, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def get_last_price(self) -> float:
        ...

    @abc.abstractmethod
    def get_stock_price_history(
        self, interval: datetime.timedelta, period: datetime.timedelta
    ) -> typing.List[model.StockHistoryDatum]:
        ...

    @abc.abstractmethod
    def get_option_chain(self, date: datetime.datetime) -> model.OptionChain:
        ...

    @abc.abstractmethod
    def get_full_option_chain(
        self
    ) -> typing.Dict[datetime.datetime, model.OptionChain]:
        ...

    @abc.abstractmethod
    def get_reddit_threads(
        self, subreddits: typing.List, time_filter: str = "day", sort: str = "hot"
    ) -> typing.List[praw.models.Submission]:
        ...


class RedditFetcher(DataProxy):
    reddit_client: praw.Reddit

    def __init__(
        self, symbol: str, *args, reddit_client: praw.Reddit = None, **kwargs
    ) -> None:
        self.symbol = symbol
        self.reddit_client = reddit_client

    def get_reddit_threads(
        self, subreddits: typing.List, time_filter: str = "day", sort: str = "hot"
    ) -> typing.List[praw.models.Submission]:
        return [
            p
            for subreddit in subreddits
            for p in self.reddit_client.subreddit(subreddit).search(
                self.symbol, time_filter=time_filter, sort=sort
            )
        ]


class YFinanceProvider(DataProxy):

    ticker: typing.Optional[yfinance.Ticker]

    def __init__(self, symbol: str, *args, **kwargs):
        self.symbol = symbol
        self.ticker = None

    def get_ticker(self) -> yfinance.Ticker:
        if not self.ticker:
            self.ticker = yfinance.Ticker(self.symbol)
        return self.ticker

    def timedelta_period_to_str(self, period: datetime.timedelta) -> str:

        if period.days == 1:
            return "1d"
        elif period.days == 5:
            return "5d"
        elif period.days == 30:
            return "1mo"
        elif period.days == 30 * 3:
            return "3mo"
        elif period.days == 30 * 6:
            return "6mo"
        elif period.days == 365:
            return "1y"
        elif period.days == 2 * 365:
            return "2y"
        elif period.days == 5 * 365:
            return "5y"
        return ""

    def timedelta_interval_to_str(self, interval: datetime.timedelta) -> str:

        if interval.seconds == 60:
            return "1m"
        elif interval.seconds == 60 * 2:
            return "2m"
        elif interval.seconds == 5 * 60:
            return "5m"
        elif interval.seconds == 15 * 60:
            return "15m"
        elif interval.seconds == 30 * 60:
            return "30m"
        elif interval.seconds == 60 * 60:
            return "60m"
        elif interval.seconds == 90 * 60:
            return "90m"
        elif interval.days == 1:
            return "1d"
        elif interval.days == 5:
            return "5d"
        elif interval.days == 7:
            return "1wk"
        elif interval.days == 30:
            return "1mo"
        elif interval.days == 90:
            return "3mo"
        return ""

    def get_last_price(self) -> float:
        data = self.get_ticker().history()
        return data.tail(1)["Close"].iloc[0]

    def get_stock_price_history(
        self, interval: datetime.timedelta, period: datetime.timedelta
    ) -> typing.List[model.StockHistoryDatum]:

        history = self.get_ticker().history(
            period=self.timedelta_period_to_str(period),
            interval=self.timedelta_interval_to_str(interval),
        )
        stock_history_data = []
        for index, row in history.iterrows():
            utc_data = int(index.replace(tzinfo=datetime.timezone.utc).timestamp())

            datum = model.StockHistoryDatum(
                symbol=self.symbol,
                time=utc_data,
                open_value=row.Open,
                close_value=row.Close,
                high=row.High,
                low=row.Low,
                volume=row.Volume,
                dividends=row.Dividends,
                stock_splits=row["Stock Splits"],
            )
            stock_history_data.append(datum)
        return stock_history_data

    def get_option_chain(self, date: datetime.datetime) -> model.OptionChain:
        date = date.replace(hour=23, minute=59, second=59)
        option_chain = self.get_ticker().option_chain(date.strftime("%Y-%m-%d"))
        current_stock_price = self.get_last_price()
        calls = [
            model.OptionChainDatum(
                type=model.OptionType.CALL,
                strike=row.strike,
                bid=row.bid,
                current_stock_price=current_stock_price,
                option_date=date,
                last_trade_date=row.lastTradeDate,
                last_price=row.lastPrice,
                open_interest=row.openInterest,
                implied_volatility=row.impliedVolatility,
                currency=row.currency,
            )
            for idx, row in option_chain.calls.iterrows()
        ]
        puts = [
            model.OptionChainDatum(
                type=model.OptionType.PUT,
                strike=row.strike,
                bid=row.bid,
                current_stock_price=current_stock_price,
                option_date=date,
                last_trade_date=row.lastTradeDate,
                last_price=row.lastPrice,
                open_interest=row.openInterest,
                implied_volatility=row.impliedVolatility,
                currency=row.currency,
            )
            for idx, row in option_chain.puts.iterrows()
        ]

        return model.OptionChain(calls=calls, puts=puts)

    def get_full_option_chain(
        self
    ) -> typing.Dict[datetime.datetime, model.OptionChain]:
        ret = {}
        current_stock_price = self.get_last_price()
        for option_expire in self.get_ticker().options:
            date = datetime.datetime.strptime(option_expire, "%Y/%m/%d")
            date = date.replace(hour=23, minute=59, second=59)
            option_chain = self.get_ticker().option_chain(option_expire)
            calls = [
                model.OptionChainDatum(
                    type=model.OptionType.CALL,
                    strike=row.strike,
                    bid=row.bid,
                    current_stock_price=current_stock_price,
                    option_date=date,
                    last_trade_date=row.lastTradeDate,
                    last_price=row.lastPrice,
                    open_interest=row.openInterest,
                    implied_volatility=row.impliedVolatility,
                    currency=row.currency,
                )
                for idx, row in option_chain.calls.iterrows()
            ]
            puts = [
                model.OptionChainDatum(
                    type=model.OptionType.PUT,
                    strike=row.strike,
                    bid=row.bid,
                    current_stock_price=current_stock_price,
                    option_date=date,
                    last_trade_date=row.lastTradeDate,
                    last_price=row.lastPrice,
                    open_interest=row.openInterest,
                    implied_volatility=row.impliedVolatility,
                    currency=row.currency,
                )
                for idx, row in option_chain.puts.iterrows()
            ]

            ret[date] = model.OptionChain(calls=calls, puts=puts)
        return ret


def combine_providers(classes: typing.List[DataProxy]) -> DataProxy:
    class CombinedProvider(*classes):
        def __init__(self, *args, **kwargs) -> None:
            for c in classes:
                c.__init__(self, *args, **kwargs)

    return CombinedProvider
