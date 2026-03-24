import os
import pandas as pd

ROOT = r"C:\Users\olivi\quant-trading-research\data"

FOLDERS = {
    "crypto": {"path": os.path.join(ROOT, "crypto"), "expected_freq": "4h"},
    "macro":  {"path": os.path.join(ROOT, "macro"),  "expected_freq": "1d"},
    "fx":     {"path": os.path.join(ROOT, "fx"),     "expected_freq": "1d"},
}

REQUIRED_COLS = ["timestamp", "open", "high", "low", "close", "volume"]

def check_file(path: str, expected_freq: str):
    issues = []

    try:
        df = pd.read_csv(path)
    except Exception as e:
        return {
            "file": os.path.basename(path),
            "rows": None,
            "start": None,
            "end": None,
            "duplicates": None,
            "missing_est": None,
            "status": f"READ_ERROR: {e}",
        }

    missing_cols = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing_cols:
        return {
            "file": os.path.basename(path),
            "rows": len(df),
            "start": None,
            "end": None,
            "duplicates": None,
            "missing_est": None,
            "status": f"MISSING_COLS: {missing_cols}",
        }

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    bad_ts = df["timestamp"].isna().sum()
    if bad_ts > 0:
        issues.append(f"bad_timestamp={bad_ts}")

    df = df.dropna(subset=["timestamp"]).copy()

    duplicates = int(df["timestamp"].duplicated().sum())
    if duplicates > 0:
        issues.append(f"duplicates={duplicates}")

    is_sorted = df["timestamp"].is_monotonic_increasing
    if not is_sorted:
        issues.append("not_sorted")

    df = df.sort_values("timestamp").reset_index(drop=True)

    start = df["timestamp"].min()
    end = df["timestamp"].max()

        missing_est = None
    if len(df) >= 2:
        diffs = df["timestamp"].diff().dropna()

        if expected_freq == "4h":
            expected = pd.Timedelta(hours=4)
            missing_est = int((diffs > expected).sum())
            if missing_est > 0:
                issues.append(f"missing_est={missing_est}")
        elif expected_freq == "1d":
            # do not flag weekend/session gaps as true missing for macro/fx daily
            missing_est = 0

    status = "OK" if not issues else "CHECK: " + "; ".join(issues)

    return {
        "file": os.path.basename(path),
        "rows": len(df),
        "start": str(start),
        "end": str(end),
        "duplicates": duplicates,
        "missing_est": missing_est,
        "status": status,
    }

def main():
    all_results = []

    for group, cfg in FOLDERS.items():
        folder = cfg["path"]
        expected_freq = cfg["expected_freq"]

        print("\n" + "=" * 80)
        print(group.upper())
        print("=" * 80)

        if not os.path.exists(folder):
            print(f"Folder does not exist: {folder}")
            continue

        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".csv")])
        if not files:
            print(f"No CSV files found in {folder}")
            continue

        for fname in files:
            path = os.path.join(folder, fname)
            result = check_file(path, expected_freq)
            all_results.append((group, result))
            print(
                f"{result['file']:<18} "
                f"rows={str(result['rows']):>6}  "
                f"dups={str(result['duplicates']):>4}  "
                f"missing_est={str(result['missing_est']):>4}  "
                f"status={result['status']}"
            )
            print(f"   start={result['start']}")
            print(f"   end  ={result['end']}")

if __name__ == "__main__":
    main()