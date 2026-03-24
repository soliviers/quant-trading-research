import os
import time
import requests
import pandas as pd

OUT_DIR = r"C:\Users\olivi\quant-trading-research\data\crypto"
os.makedirs(OUT_DIR, exist_ok=True)

BASE_URL = "https://fapi.binance.com/fapi/v1/klines"

SYMBOLS = {
    "BTCUSDT": "2019-01-01",
    "ETHUSDT": "2019-01-01",
    "SOLUSDT": "2020-01-01",
    "AVAXUSDT": "2020-01-01",
    "XRPUSDT": "2019-01-01",
    "BNBUSDT": "2019-01-01",
    "ADAUSDT": "2019-01-01",
    "DOGEUSDT": "2019-01-01",
    "LINKUSDT": "2019-01-01",
    "ARBUSDT": "2023-01-01",
    "OPUSDT":  "2022-01-01",
    "INJUSDT": "2021-01-01",
}

INTERVAL = "4h"
LIMIT = 1500

def to_ms(dt_str: str) -> int:
    return int(pd.Timestamp(dt_str, tz="UTC").timestamp() * 1000)

def fetch_all_klines(symbol: str, start_date: str, interval: str = "4h") -> pd.DataFrame:
    start_ms = to_ms(start_date)
    all_rows = []

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "limit": LIMIT,
        }
        r = requests.get(BASE_URL, params=params, timeout=30)
        r.raise_for_status()
        rows = r.json()

        if not rows:
            break

        all_rows.extend(rows)

        last_open_time = rows[-1][0]
        next_start = last_open_time + 1

        if next_start <= start_ms:
            break

        start_ms = next_start

        if len(rows) < LIMIT:
            break

        time.sleep(0.2)

    if not all_rows:
        return pd.DataFrame()

    cols = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ]
    df = pd.DataFrame(all_rows, columns=cols)

    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df

def main():
    for symbol, start_date in SYMBOLS.items():
        print(f"Downloading {symbol} from {start_date}...")
        df = fetch_all_klines(symbol, start_date, INTERVAL)

        if df.empty:
            print(f"  -> No data returned for {symbol}")
            continue

        out_path = os.path.join(OUT_DIR, f"{symbol}_4h.csv")
        df.to_csv(out_path, index=False)
        print(f"  -> Saved {len(df):,} rows to {out_path}")

if __name__ == "__main__":
    main()