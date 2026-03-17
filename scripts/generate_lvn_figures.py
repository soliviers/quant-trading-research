import pandas as pd
import matplotlib.pyplot as plt

# Paths (adjust if needed)
base_path = r"C:\Users\olivi\lvn-auction-backtester\friction_results"
output_path = r"C:\Users\olivi\quant-trading-research\projects\strategy_backtesting\lvn_auction_friction_review\figures"

# Load data
fm = pd.read_csv(f"{base_path}/friction_matrix.csv")
cmp = pd.read_csv(f"{base_path}/candidate_friction_comparison.csv")

# -----------------------------
# 1. Friction PF chart
# -----------------------------
plt.figure()
plt.plot(fm["scenario"], fm["pf"], marker='o')
plt.xticks(rotation=45)
plt.xlabel("Scenario")
plt.ylabel("Profit Factor (PF)")
plt.title("Friction Sensitivity — Profit Factor")
plt.tight_layout()
plt.savefig(f"{output_path}/friction_pf.png")
plt.close()

# -----------------------------
# 2. Friction Avg PnL chart
# -----------------------------
plt.figure()
plt.plot(fm["scenario"], fm["avg_pnl"], marker='o')
plt.xticks(rotation=45)
plt.xlabel("Scenario")
plt.ylabel("Average PnL")
plt.title("Friction Sensitivity — Avg PnL")
plt.tight_layout()
plt.savefig(f"{output_path}/friction_avg_pnl.png")
plt.close()

# -----------------------------
# 3. Candidate comparison
# -----------------------------
plt.figure()
plt.bar(cmp["candidate"], cmp["pf"])
plt.xticks(rotation=45)
plt.xlabel("Candidate")
plt.ylabel("Profit Factor (PF)")
plt.title("Candidate Comparison Under Friction")
plt.tight_layout()
plt.savefig(f"{output_path}/candidate_pf.png")
plt.close()

print("Figures generated successfully.")