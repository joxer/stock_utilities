import datetime

import stock_utilities

data = stock_utilities.stock_data.StockData(
    "SPY", stock_utilities.proxy.YFinanceProvider
)
print(data.get_last_price())
data = stock_utilities.stock_data.StockData(
    "SPY", stock_utilities.proxy.YFinanceProvider
)
history = data.get_stock_price_history(
    interval=datetime.timedelta(days=1), period=datetime.timedelta(days=5)
)
assert len(history), 5

history_option = data.get_next_friday_option_chain()

print(history_option.calls[-1].delta(), history_option.calls[-1].vega())