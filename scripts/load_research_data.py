import os
import json
from typing import Dict, Tuple

import pandas as pd

DATA_ROOT = r"C:\Users\olivi\quant-trading-research\data"
MANIFEST_PATH = os.path.join(DATA_ROOT, "data_manifest.json")

REQUIRED_COLS = ["timestamp", "open", "high", "low", "close", "volume"]

def load_manifest(path: str = MANIFEST_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def infer_symbol_from_filename(fname: str) -> str:
    return fname.replace(".csv", "")

def load_single_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"{os.path.basename(path)} missing columns: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="raise")

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="raise")

    df = (
        df[REQUIRED_COLS]
        .drop_duplicates(subset=["timestamp"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    return df

def load_bucket(bucket_name: str) -> Dict[str, pd.DataFrame]:
    manifest = load_manifest()

    if bucket_name not in manifest:
        raise ValueError(f"Unknown bucket: {bucket_name}. Available: {list(manifest.keys())}")

    datasets = {}

    for item in manifest[bucket_name]:
        fname = item["file"]
        path = item["path"]
        symbol = infer_symbol_from_filename(fname)

        df = load_single_csv(path)
        datasets[symbol] = df

    return datasets

def get_overlap_window(datasets: Dict[str, pd.DataFrame]) -> Tuple[pd.Timestamp, pd.Timestamp]:
    starts = [df["timestamp"].min() for df in datasets.values()]
    ends = [df["timestamp"].max() for df in datasets.values()]

    overlap_start = max(starts)
    overlap_end = min(ends)

    if overlap_start >= overlap_end:
        raise ValueError("No valid overlap window across datasets.")

    return overlap_start, overlap_end

def trim_to_overlap(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    overlap_start, overlap_end = get_overlap_window(datasets)

    trimmed = {}
    for symbol, df in datasets.items():
        out = df[(df["timestamp"] >= overlap_start) & (df["timestamp"] <= overlap_end)].copy()
        out = out.reset_index(drop=True)
        trimmed[symbol] = out

    return trimmed

def summarize_bucket(datasets: Dict[str, pd.DataFrame], title: str):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    for symbol, df in sorted(datasets.items()):
        print(
            f"{symbol:<18} rows={len(df):>6}  "
            f"start={df['timestamp'].min()}  "
            f"end={df['timestamp'].max()}"
        )

def main():
    # Example usage
    crypto = load_bucket("crypto_4h")
    summarize_bucket(crypto, "CRYPTO_4H — RAW")

    crypto_overlap = trim_to_overlap(crypto)
    summarize_bucket(crypto_overlap, "CRYPTO_4H — OVERLAP TRIMMED")

    macro = load_bucket("macro_1d")
    summarize_bucket(macro, "MACRO_1D — RAW")

    fx = load_bucket("fx_1d")
    summarize_bucket(fx, "FX_1D — RAW")

if __name__ == "__main__":
    main()