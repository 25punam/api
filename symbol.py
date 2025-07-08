from brokers.flattrade.api import FlatTradeApiPy

# True = Paper Trading
api = FlatTradeApiPy(emulation=True)

df = api.instruments("BSE")
print(df.columns.tolist())
print(df.columns)


#['exchange', 'instrument_token', 'lot_size', 'name', 'tradingsymbol', 'segment', 'tick_size']