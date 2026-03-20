from __future__ import annotations

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def validate_file(path: Path, expected_24_7: bool) -> dict:
    df = pd.read_csv(path)
    required = ["timestamp", "open", "high", "low", "close", "volume"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        return {
            "file": str(path),
            "status": "FAIL",
            "reason": f"missing columns: {missing_cols}",
        }

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")

    duplicated = int(df["timestamp"].duplicated().sum())
    monotonic = bool(df["timestamp"].is_monotonic_increasing)

    if expected_24_7 and len(df) > 0:
        expected = pd.date_range(df["timestamp"].min(), df["timestamp"].max(), freq="4h", tz="UTC")
        missing_bars = len(expected.difference(pd.DatetimeIndex(df["timestamp"])))
    else:
        missing_bars = -1

    return {
        "file": str(path),
        "status": "OK" if duplicated == 0 and monotonic else "FAIL",
        "rows": len(df),
        "duplicated_timestamps": duplicated,
        "monotonic": monotonic,
        "missing_bars": missing_bars,
        "start": df["timestamp"].min() if len(df) else None,
        "end": df["timestamp"].max() if len(df) else None,
    }


def main() -> None:
    rows = []

    for folder in ["crypto", "macro", "fx"]:
        folder_path = DATA_DIR / folder
        if not folder_path.exists():
            continue

        for path in sorted(folder_path.glob("*.csv")):
            rows.append(validate_file(path, expected_24_7=(folder == "crypto")))

    out = pd.DataFrame(rows)
    if len(out):
        print(out.to_string(index=False))
    else:
        print("No CSV files found under data/.")


if __name__ == "__main__":
    main()