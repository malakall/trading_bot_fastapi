import ccxt
import pandas as pd

exchange = ccxt.binance()

def get_candles(symbol: str, timeframe: str, limit=100):
    data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df