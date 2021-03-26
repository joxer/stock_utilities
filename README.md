# stock_utilities

This repo will manage utilities for stock data and stock option
The idea is to fetch data from multiple sources and use them from a single point and have a library that is typesafe


The used provider are:
  - YFinance

## Example

```
import datetime
import praw
import stock_utilities

data = stock_utilities.stock_data.StockData(
    "GME", stock_utilities.proxy.YFinanceProvider
)
print(data.get_last_price())
data = stock_utilities.stock_data.StockData(
    "GME", stock_utilities.proxy.YFinanceProvider
)
history = data.get_stock_price_history(
    interval=datetime.timedelta(days=1), period=datetime.timedelta(days=5)
)
assert len(history), 5

history_option = data.get_next_friday_option_chain()
print(history_option.calls[-1])
print(
    history_option.calls[-1].delta(),
    history_option.calls[-1].gamma(),
    history_option.calls[-1].vega(),
)


combined_providers = stock_utilities.proxy.combine_providers(
    [stock_utilities.proxy.YFinanceProvider, stock_utilities.proxy.RedditFetcher]
)

reddit = praw.Reddit(
   client_id="XXX",
   client_secret="XXX",
   user_agent="XXX",
)
new_client = stock_utilities.stock_data.StockData(
   "GME", combined_providers, reddit_client=reddit
)

print(new_client.get_reddit_threads(["wallstreetbets"]))
```