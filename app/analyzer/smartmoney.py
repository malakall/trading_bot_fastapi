import ccxt
from .fetcher import get_candles

binance_futures = ccxt.binance({
    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})

def detect_order_block(df):
    ob_type = None
    ob_top = None
    ob_bottom = None

    c2_open = df['open'].iloc[-3]
    c2_close = df['close'].iloc[-3]
    c2_high = df['high'].iloc[-3]
    c2_low = df['low'].iloc[-3]

    c1_high = df['high'].iloc[-4]
    c1_low = df['low'].iloc[-4]

    if c2_close > c2_open:
        ob_type = "bullish"
        ob_top = c2_high
        ob_bottom = min(c2_low, c1_low)
    elif c2_close < c2_open:
        ob_type = "bearish"
        ob_top = max(c2_high, c1_high)
        ob_bottom = c2_low

    return {
        "type": ob_type,
        "top": round(ob_top, 2) if ob_top else None,
        "bottom": round(ob_bottom, 2) if ob_bottom else None
    }

def get_funding(symbol: str):
    try:
        funding = binance_futures.fetch_funding_rate(symbol)
        return {
            "rate": f"{funding['fundingRate'] * 100:.6f}",
            "next_funding_time": funding.get("nextFundingTimestamp"),
            "timestamp": funding['timestamp'],
        }
    except Exception as e:
        return {
            "rate": None,
            "error": str(e)
        }


def smartmoney_analysis(symbol: str, timeframe: str):
    df = get_candles(symbol, timeframe)

    highs = df['high']
    lows = df['low']
    closes = df['close']
    opens = df['open']
    volumes = df['volume'] if 'volume' in df.columns else None

    bos = None
    if closes.iloc[-1] > highs.iloc[-2]:
        bos = "Break of structure ↑"
    elif closes.iloc[-1] < lows.iloc[-2]:
        bos = "Break of structure ↓"
    else:
        bos = "No BOS"

    ob_data = detect_order_block(df)

    fvg = None
    if highs.iloc[-3] < lows.iloc[-1]:
        fvg = (round(highs.iloc[-3], 2), round(lows.iloc[-1], 2))
    elif lows.iloc[-3] > highs.iloc[-1]:
        fvg = (round(lows.iloc[-3], 2), round(highs.iloc[-1], 2))

    breaker_block = None
    if closes.iloc[-2] > highs.iloc[-4]:
        breaker_block = (highs.iloc[-4] + lows.iloc[-4]) / 2

    liquidity = {
        "above": round(highs.iloc[-10:].max(), 2),
        "below": round(lows.iloc[-10:].min(), 2)
    }

    volume_info = volumes.iloc[-1] if volumes is not None else "n/a"

    # Получаем фандинг
    funding_info = get_funding(symbol.replace("/", ""))  # Binance требует формат без слэша: BTCUSDT

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "signal": bos,
        "entry_zone": ob_data["bottom"],
        "last_price": round(closes.iloc[-1], 2),
        "fvg": fvg,
        "breaker_block": round(breaker_block, 2) if breaker_block else None,
        "liquidity": liquidity,
        "volume": volume_info,
        "order_block_type": ob_data["type"],
        "order_block_range": (ob_data["top"], ob_data["bottom"]) if ob_data["top"] and ob_data["bottom"] else None,
        "funding_rate_%": funding_info["rate"],
        "funding_timestamp": funding_info.get("timestamp"),
        "funding_error": funding_info.get("error")  # На случай ошибки
    }
