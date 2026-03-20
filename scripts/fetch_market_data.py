from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import ccxt
import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

CRYPTO_ASSETS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "AVAX/USDT",
    "XRP/USDT",
]

# Temporarily disabled because Yahoo intraday history is capped
# and does not support 1h back to 2019.
MACRO_ASSETS: list[str] = []
FX_ASSETS: list[str] = []

TIMEFRAME = "4h"
START_DATE = "2019-01-01T00:00:00Z"
BINANCE_LIMIT = 1000


@dataclass
class FetchSummary:
    symbol: str
    asset_class: str
    rows: int
    start: Optional[pd.Timestamp]
    end: Optional[pd.Timestamp]
    duplicates_removed: int
    missing_bars: Optional[int]
    path: Path


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def standardize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    required = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp")
    out = out.drop_duplicates(subset=["timestamp"], keep="last")
    out = out[required]
    out = out.set_index("timestamp")
    return out


def validate_ohlcv(
    df: pd.DataFrame,
    freq: str,
    expected_24_7: bool,
) -> tuple[int, int]:
    if not df.index.is_monotonic_increasing:
        raise ValueError("Timestamp index is not monotonic increasing")

    duplicates = int(df.index.duplicated().sum())
    if duplicates > 0:
        raise ValueError(f"Found duplicated timestamps after cleaning: {duplicates}")

    if expected_24_7:
        expected = pd.date_range(df.index.min(), df.index.max(), freq=freq, tz="UTC")
        missing = len(expected.difference(df.index))
    else:
        missing = -1

    return duplicates, missing


def save_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    df.to_csv(path, index=False)


def symbol_to_filename(symbol: str) -> str:
    return symbol.replace("/", "").replace("=X", "").replace("^", "")


def load_existing(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return standardize_ohlcv(df)


def merge_existing_and_new(existing: Optional[pd.DataFrame], new_df: pd.DataFrame) -> pd.DataFrame:
    if existing is None or existing.empty:
        return new_df
    merged = pd.concat([existing, new_df]).sort_index()
    merged = merged[~merged.index.duplicated(keep="last")]
    return merged


def fetch_binance_ohlcv(symbol: str, since_iso: str = START_DATE) -> pd.DataFrame:
    exchange = ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })

    since = exchange.parse8601(since_iso)
    all_rows = []

    while True:
        batch = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, since=since, limit=BINANCE_LIMIT)
        if not batch:
            break

        all_rows.extend(batch)

        last_ts = batch[-1][0]
        next_since = last_ts + 1

        if next_since <= since:
            break

        since = next_since

        if len(batch) < BINANCE_LIMIT:
            break

        time.sleep(exchange.rateLimit / 1000)

    if not all_rows:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(all_rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return standardize_ohlcv(df.reset_index(drop=True))


def fetch_yfinance_ohlcv(symbol: str, start: str = "2019-01-01") -> pd.DataFrame:
    """
    Kept here for later use, but not active in main() right now.

    Yahoo intraday history is capped, so 1h data back to 2019 will fail.
    This function remains for future adaptation if you decide to:
    - fetch only the last ~730 days, or
    - use a different provider for macro/fx.
    """
    df = yf.download(
        symbol,
        interval="1h",
        start=start,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    df = df[["open", "high", "low", "close", "volume"]].copy()

    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")

    agg = (
        df.resample("4h", label="left", closed="left")
        .agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        })
        .dropna()
    )

    agg.index.name = "timestamp"
    agg = agg.reset_index()
    return standardize_ohlcv(agg)


def fetch_and_store_crypto(symbol: str) -> FetchSummary:
    path = DATA_DIR / "crypto" / f"{symbol_to_filename(symbol)}_4h.csv"
    existing = load_existing(path)

    since_iso = START_DATE
    if existing is not None and not existing.empty:
        last_ts = existing.index.max()
        since_iso = (last_ts - pd.Timedelta(days=5)).isoformat()

    new_df = fetch_binance_ohlcv(symbol, since_iso=since_iso)
    merged = merge_existing_and_new(existing, new_df)

    before = len(merged)
    merged = merged[~merged.index.duplicated(keep="last")]
    duplicates_removed = before - len(merged)

    _, missing_bars = validate_ohlcv(merged, freq="4h", expected_24_7=True)
    save_csv(merged.reset_index(), path)

    return FetchSummary(
        symbol=symbol,
        asset_class="crypto",
        rows=len(merged),
        start=merged.index.min() if len(merged) else None,
        end=merged.index.max() if len(merged) else None,
        duplicates_removed=duplicates_removed,
        missing_bars=missing_bars,
        path=path,
    )


def fetch_and_store_yf(symbol: str, asset_class: str) -> FetchSummary:
    path = DATA_DIR / asset_class / f"{symbol_to_filename(symbol)}_4h.csv"
    existing = load_existing(path)

    new_df = fetch_yfinance_ohlcv(symbol)
    merged = merge_existing_and_new(existing, new_df)

    before = len(merged)
    merged = merged[~merged.index.duplicated(keep="last")]
    duplicates_removed = before - len(merged)

    _, missing_bars = validate_ohlcv(merged, freq="4h", expected_24_7=False)
    save_csv(merged.reset_index(), path)

    return FetchSummary(
        symbol=symbol,
        asset_class=asset_class,
        rows=len(merged),
        start=merged.index.min() if len(merged) else None,
        end=merged.index.max() if len(merged) else None,
        duplicates_removed=duplicates_removed,
        missing_bars=missing_bars,
        path=path,
    )


def print_summary(summaries: list[FetchSummary]) -> None:
    rows = []
    for s in summaries:
        rows.append({
            "asset_class": s.asset_class,
            "symbol": s.symbol,
            "rows": s.rows,
            "start": s.start,
            "end": s.end,
            "duplicates_removed": s.duplicates_removed,
            "missing_bars": s.missing_bars,
            "path": str(s.path),
        })
    out = pd.DataFrame(rows)
    print(out.to_string(index=False))


def main() -> None:
    summaries: list[FetchSummary] = []

    for symbol in CRYPTO_ASSETS:
        summaries.append(fetch_and_store_crypto(symbol))

    # Macro/FX intentionally skipped for now because Yahoo 1h history
    # does not go back far enough for this research window.

    print_summary(summaries)


if __name__ == "__main__":
    main()