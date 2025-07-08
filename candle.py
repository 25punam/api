from brokers.flattrade.api import FlatTradeApiPy
from datetime import datetime, timedelta


# True = Paper Trading
api_obj = FlatTradeApiPy(emulation=True)


print(api_obj.instruments())


curr_date = datetime.today()
from_date = curr_date - timedelta(days=1)
res = api_obj.historical_data("36840", from_date, curr_date, interval="minute", return_df=True)
print(res)