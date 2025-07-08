from brokers.flattrade.api import FlatTradeApiPy
from login import api
import pandas as pd
import datetime
from tabulate import tabulate
import csv,os


api = FlatTradeApiPy(emulation=True)
# CSV_FILE = "stock_list.csv"


CSV_FILE       = "mini_test_stock_list.csv"
TARGET_PCT     = 1          # +1 %
STOPLOSS_PCT   = 1          # –1 %
INTERVAL_MIN   = 15         # candle size

# ───────────────────────────────────────────────────────────────
# 1️⃣  Read alert list
# ───────────────────────────────────────────────────────────────
entries = []
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"{CSV_FILE} not found")

with open(CSV_FILE, newline="", encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    for row in rdr:
        sym     = row["symbol"].strip().upper()
        mcap    = row["marketcapname"].strip()
        sector  = row["sector"].strip()
        dt_str  = row["date"].strip().upper()

        # accept “dd-mm-yyyy HH:MM AM/PM”  OR  “dd-mm-yyyy”
        try:
            entry_dt = datetime.datetime.strptime(dt_str, "%d-%m-%Y %I:%M %p")
        except ValueError:
            entry_dt = datetime.datetime.strptime(dt_str, "%d-%m-%Y")

        # only alerts between 09 :30 and 14 :30
        if not (datetime.time(9,30) <= entry_dt.time() <= datetime.time(14,30)):
            continue

        entries.append({"symbol": sym,
                        "entry_dt": entry_dt,
                        "mcap": mcap,
                        "sector": sector})

# ───────────────────────────────────────────────────────────────
# 2️⃣  NSE master once → token + tradingsymbol look‑up
# ───────────────────────────────────────────────────────────────
df_nse = api.instruments("NSE")     # DataFrame with columns name, tradingsymbol, instrument_token …

# helper for token
def get_token(sym: str):
    r = df_nse[df_nse["name"] == sym]        # exact match first
    if r.empty:
        r = df_nse[df_nse["tradingsymbol"].str.contains(sym)]
    return None if r.empty else (r.iloc[0]["instrument_token"],
                                 r.iloc[0]["tradingsymbol"])

# candle hit checks
def tgt_hit(ep, cp, tgt): return cp >= tgt
def sl_hit(ep, cp, sl):  return cp <= sl


rows = []

for item in entries:
    sym, entry_dt = item["symbol"], item["entry_dt"]
    mcap, sector   = item["mcap"],   item["sector"]

    token_pair = get_token(sym)
    print(token_pair)
    if not token_pair:
        continue
    token, tradingsymbol = token_pair

    # candle range: entry alert -> 15 :30 same day
    end_dt     = datetime.datetime.combine(entry_dt.date(), datetime.time(15,30))
    ts_start   = int(entry_dt.timestamp())
    ts_end     = int(end_dt.timestamp())

    # ── 2‑minute => 120 sec, 5‑minute => 300 sec; Flattrade expects secs
    try:
        candles = api.get_time_price_series("NSE",
                                            token,
                                            starttime=ts_start,
                                            endtime=ts_end,
                                            interval=INTERVAL_MIN)   # returns list newest→oldest
    except Exception:
        continue

    if not candles:
        continue
    candles = candles[::-1]   # oldest→newest for forward scan

    entry_price = float(candles[0]["intc"])          # close of first candle
    entry_time  = entry_dt.strftime("%I:%M %p")

    tgt_price   = round(entry_price * (1 + TARGET_PCT/100), 2)
    sl_price    = round(entry_price * (1 - STOPLOSS_PCT/100), 2)

    exit_price, exit_time, status = "-", "-", "Not Hit"

    # ──────────────────────────────
    # hit‑scan candle‑by‑candle
    # ──────────────────────────────
    for c in candles:
        cp = float(c["intc"])
        ct = datetime.datetime.strptime(c["time"], "%d-%m-%Y %H:%M:%S")
        ct_fmt = ct.strftime("%I:%M %p")

        if tgt_hit(entry_price, cp, tgt_price):
            exit_price, exit_time, status = cp, ct_fmt, "Target Hit"
            break
        if sl_hit(entry_price, cp, sl_price):
            exit_price, exit_time, status = cp, ct_fmt, "Stoploss Hit"
            break

    # Square‑off 15 :15 if nothing hit & alert before 15 :15
    if status == "Not Hit" and entry_dt.time() < datetime.time(15,15):
        sq_str = f"{entry_dt.strftime('%d-%m-%Y')} 15:15:00"
        sq = next((c for c in candles if c["time"] == sq_str), None)
        if sq:
            exit_price = float(sq["intc"])
            exit_time  = "03:15 PM"
            status = "Square‑off Profit" if exit_price > entry_price else "Square‑off Loss"

    # P&L
    pl = "-"
    if isinstance(exit_price, (int, float, float)):
        diff = round(exit_price - entry_price, 2)
        pl = f"+{diff}" if diff > 0 else f"{diff}"

    
    try:
        order_id, ok = api.place_order(tradingsymbol=tradingsymbol,
                                       transaction_type="BUY",
                                       order_type="MKT",
                                       quantity=1,
                                       price=0.0)
        order_status = "Order Placed" if ok else "Order Rejected"
    except Exception as e:
        order_status = f"Order Failed: {e}"

    rows.append([
        entry_dt.strftime("%d-%m-%Y"),
        sym, mcap, sector,
        entry_time, entry_price, tgt_price, sl_price,
        exit_price, exit_time, status, pl, order_status
    ])


headers = ["Date","Symbol","MCap","Sector","Entry Time","Entry Price",
           "Target","Stop Loss","Exit Price","Exit Time",
           "Status","Profit/Loss","Order Place"]


# df = pd.DataFrame(rows, columns=headers)
# print(tabulate(df, headers=headers, tablefmt="plain"))
