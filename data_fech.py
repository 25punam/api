from brokers.flattrade.api import FlatTradeApiPy
from datetime import datetime, timedelta


# True = Paper Trading
api = FlatTradeApiPy(emulation=True)

# Instruments list fetch karo


symbols = ["SBIN", "NHPC", "RELIANCE", "INFY"]
df = api.instruments("NSE")

for sym in symbols:
    row = df[df["tradingsymbol"].str.contains(sym)]
    if not row.empty:
        token = row.iloc[0]["instrument_token"]
        print(f"{sym} → Token: {token}")
    else:
        print(f"{sym} → ❌ Not found")


# SBIN → Token: 24524
# NHPC → Token: 17400
# RELIANCE → Token: 2885
# INFY → Token: 1594