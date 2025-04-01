import ccxt
import pandas as pd
import talib
import time

def fetch_data(exchange, symbol, timeframe='1h', limit=100):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv:
            print("Erreur: Pas de données récupérées.")
            return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return None

def calculate_indicators(df):
    if df is None or df.empty:
        return None
    df['rsi'] = talib.RSI(df['close'], timeperiod=14).fillna(0)
    df['macd'], df['signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['macd'] = df['macd'].fillna(0)
    df['signal'] = df['signal'].fillna(0)
    return df

def trading_signal(df):
    if df is None or df.empty:
        return "NO DATA"
    latest = df.iloc[-1]
    if latest['rsi'] < 30 and latest['macd'] > latest['signal']:
        return "BUY"
    elif latest['rsi'] > 70 and latest['macd'] < latest['signal']:
        return "SELL"
    return "HOLD"

def main():
    exchange = ccxt.binance()
    exchange.load_markets()
    symbol = 'BTC/USDT'  # Changer pour une action si disponible sur Binance
    timeframe = '1h'
    
    while True:
        df = fetch_data(exchange, symbol, timeframe)
        if df is not None:
            df = calculate_indicators(df)
            signal = trading_signal(df)
            print(f"{df['timestamp'].iloc[-1] if df is not None else 'N/A'} - Signal: {signal}")
        else:
            print("Données non disponibles, tentative dans 60 secondes...")
        time.sleep(60)  # Rafraîchit toutes les minutes

if __name__ == "__main__":
    main()
