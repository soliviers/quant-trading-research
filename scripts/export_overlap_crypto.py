import os
from load_research_data import load_bucket, trim_to_overlap

OUT_DIR = r"C:\Users\olivi\quant-trading-research\data\crypto_overlap_4h"
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    crypto = load_bucket("crypto_4h")
    trimmed = trim_to_overlap(crypto)

    for symbol, df in trimmed.items():
        out_path = os.path.join(OUT_DIR, f"{symbol}.csv")
        df.to_csv(out_path, index=False)
        print(f"Saved {symbol}: {len(df)} rows -> {out_path}")

if __name__ == "__main__":
    main()