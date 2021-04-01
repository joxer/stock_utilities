import datetime
import praw
import stock_utilities

data_proxy = stock_utilities.stock_data.StockData(
    "GME", stock_utilities.proxy.YFinanceProvider  # , proxy="127.0.0.1:9080"
)
# print(data_proxy.get_last_price())

h1 = data_proxy.get_stock_price_history(
    interval=datetime.timedelta(minutes=30), period=datetime.timedelta(days=30)
)
print(h1)
# print(data_proxy.get_info())
history_option = data_proxy.get_next_option_chain()
# print(history_option.calls[-1])
# print(
#    history_option.calls[-1].delta(),
#    history_option.calls[-1].gamma(),
#    history_option.calls[-1].vega(),
# )


# combined_providers = stock_utilities.proxy.combine_providers(
#    [stock_utilities.proxy.YFinanceProvider, stock_utilities.proxy.RedditFetcher]
# )

# reddit = praw.Reddit(client_id="XXX", client_secret="XXX", user_agent="XXX")
# new_client = stock_utilities.stock_data.StockData(
#    "GME", combined_providers, reddit_client=reddit
# )

# print(new_client.get_reddit_threads(["wallstreetbets"]))


data_proxy = stock_utilities.stock_data.StockData(
    "RKT", stock_utilities.proxy.YFinanceProvider  # , proxy="127.0.0.1:9080"
)

h2 = data_proxy.get_stock_price_history(
    interval=datetime.timedelta(minutes=30), period=datetime.timedelta(days=30)
)

# print(stock_utilities.correlation.correlation_history(h1, h2))
