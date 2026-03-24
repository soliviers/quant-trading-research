import os
import json
import pandas as pd

ROOT = r"C:\Users\olivi\quant-trading-research\data"

GROUPS = {
    "crypto_4h": os.path.join(ROOT, "crypto"),
    "macro_1d": os.path.join(ROOT, "macro"),
    "fx_1d": os.path.join(ROOT, "fx"),
}

def main():
    manifest = {}

    for group, folder in GROUPS.items():
        manifest[group] = []

        for fname in sorted(os.listdir(folder)):
            if not fname.lower().endswith(".csv"):
                continue

            path = os.path.join(folder, fname)
            df = pd.read_csv(path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
            df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

            manifest[group].append({
                "file": fname,
                "path": path,
                "rows": int(len(df)),
                "start": str(df["timestamp"].min()),
                "end": str(df["timestamp"].max()),
                "columns": list(df.columns),
            })

    out_path = r"C:\Users\olivi\quant-trading-research\data\data_manifest.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Saved manifest to: {out_path}")

if __name__ == "__main__":
    main()