from brokers.flattrade.api import FlatTradeApiPy
from login import api
import pandas as pd
import datetime,tabulate
import time

#  True = Paper Trading
api = FlatTradeApiPy(emulation=True)


symbols = [
    "AKSHARCHEM", "REPRO", "NHPC", "GMDCLTD", "ALLDIGI", "SJS",
    "HGS", "PNGJL", "LAGNAM", "RKDL", "DEVYANI", "CARRARO"
]

dummy_rejected = ["NHPC", "LAGNAM", "DEVYANI"]  

TRANSACTION_TYPE = "SELL"
ORDER_TYPE = "LIMIT"
QTY = 1
LIMIT_PRICE = 50

df_nse = api.instruments("NSE")
records = []

for sym in symbols:
    row = df_nse[df_nse["name"] == sym]
    if row.empty:
        records.append({
            "Symbol": sym,
            "Token": "-",
            "Txn": TRANSACTION_TYPE,
            "Order-Type": ORDER_TYPE,
            "Qty": QTY,
            "Price": LIMIT_PRICE,
            "Order-ID": "-",
            "Status": "Not in NSE list"
        })
        continue

    token = row.iloc[0]["instrument_token"]
    tradingsymbol = row.iloc[0]["tradingsymbol"]


    if sym in dummy_rejected:
        records.append({
            "Symbol": sym,
            "Token": token,
            "Txn": TRANSACTION_TYPE,
            "Order-Type": ORDER_TYPE,
            "Qty": QTY,
            "Price": LIMIT_PRICE,
            "Order-ID": f"REJ_{sym}",
            "Status": "Rejected"
        })
        continue

    try:
        order_id, ok = api.place_order(
            tradingsymbol=tradingsymbol,
            transaction_type=TRANSACTION_TYPE,
            order_type=ORDER_TYPE,
            quantity=QTY,
            price=LIMIT_PRICE
        )
        status = "Placed" if ok else "Rejected"
    except Exception as e:
        order_id, status = "-", f"Error: {str(e)}"

    records.append({
        "Symbol": sym,
        "Token": token,
        "Txn": TRANSACTION_TYPE,
        "Order-Type": ORDER_TYPE,
        "Qty": QTY,
        "Price": LIMIT_PRICE,
        "Order-ID": order_id,
        "Status": status
    })


df = pd.DataFrame(records)
print(df.to_string(index=False))


'''    Symbol  Token  Txn Order-Type  Qty  Price       Order-ID   Status
AKSHARCHEM  20178 SELL      LIMIT   10    500 20052000000017   Placed
     REPRO  13126 SELL      LIMIT   10    500 20052000000017   Placed
      NHPC  17400 SELL      LIMIT   10    500       REJ_NHPC Rejected
   GMDCLTD   5204 SELL      LIMIT   10    500 20052000000017   Placed
   ALLDIGI  11798 SELL      LIMIT   10    500 20052000000017   Placed
       SJS   6643 SELL      LIMIT   10    500 20052000000017   Placed
       HGS  14712 SELL      LIMIT   10    500 20052000000017   Placed
     PNGJL  25312 SELL      LIMIT   10    500 20052000000017   Placed
    LAGNAM   5865 SELL      LIMIT   10    500     REJ_LAGNAM Rejected
      RKDL  20950 SELL      LIMIT   10    500 20052000000017   Placed
   DEVYANI   5373 SELL      LIMIT   10    500    REJ_DEVYANI Rejected
   CARRARO  28879 SELL      LIMIT   10    500 20052000000017   Placed'''