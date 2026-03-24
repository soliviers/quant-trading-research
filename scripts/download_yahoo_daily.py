import os
import pandas as pd
import yfinance as yf

ROOT = r"C:\Users\olivi\quant-trading-research\data"
MACRO_DIR = os.path.join(ROOT, "macro")
FX_DIR = os.path.join(ROOT, "fx")

os.makedirs(MACRO_DIR, exist_ok=True)
os.makedirs(FX_DIR, exist_ok=True)

macro_assets = {
    "SPY": "SPY",
    "QQQ": "QQQ",
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "GOLD": "GC=F",
}

fx_assets = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "JPY=X",
}

def download_daily(ticker: str, start: str = "2019-01-01") -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=start,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    df.index = pd.to_datetime(df.index, utc=True)
    df = df.reset_index().rename(columns={"Date": "timestamp", "Datetime": "timestamp"})

    keep = ["timestamp", "open", "high", "low", "close"]
    if "volume" in df.columns:
        keep.append("volume")
    else:
        df["volume"] = 0
        keep.append("volume")

    df = df[keep].dropna(subset=["timestamp", "open", "high", "low", "close"])
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    return df

def main():
    for name, ticker in macro_assets.items():
        print(f"Downloading macro {name} ({ticker}) daily...")
        df = download_daily(ticker)
        out = os.path.join(MACRO_DIR, f"{name}_1d.csv")
        df.to_csv(out, index=False)
        print(f"  -> Saved {len(df):,} rows to {out}")

    for name, ticker in fx_assets.items():
        print(f"Downloading FX {name} ({ticker}) daily...")
        df = download_daily(ticker)
        out = os.path.join(FX_DIR, f"{name}_1d.csv")
        df.to_csv(out, index=False)
        print(f"  -> Saved {len(df):,} rows to {out}")

if __name__ == "__main__":
    main()