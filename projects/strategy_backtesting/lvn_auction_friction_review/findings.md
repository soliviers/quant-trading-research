# Findings — LVN Auction Backtest (1H Structure + 15m Execution)

## 1. Overview

This research evaluated a mean-reversion strategy based on Auction Market Theory, specifically targeting reactions from Low Volume Nodes (LVNs) back toward the developing Point of Control (POC).

The system combined:

- **1H timeframe** for structural context (volume profile, LVNs, value area)
- **15m timeframe** for execution (entry, stop, and exit logic)

The objective was to determine whether this framework produces a **robust, execution-viable trading edge**.

---

## 2. Key Positive Findings

### 2.1 Value Area Containment is a Strong Filter

Performance improved consistently as the system required stronger value-area acceptance.

- Best-performing candidates clustered around:
  - `va_containment_threshold = 0.60–0.65`

This suggests that **contextual auction acceptance** is a meaningful prerequisite for LVN-based trades.

---

### 2.2 Edge Concentration Around Moderate Entry Thresholds

The most effective parameter range was:

- `min_edge_bps = 30–35`

Lower thresholds increased trade frequency but reduced robustness.  
Higher thresholds reduced opportunities without consistently improving performance.

---

### 2.3 Dual-Timeframe Architecture Adds Signal Quality

Using:

- **1H for structure**
- **15m for execution**

allowed the system to capture rejection behavior that was invisible in 1H-only backtests.

This confirmed that **execution resolution materially impacts observed edge**.

---

## 3. Best Zero-Friction Candidate

The strongest configuration identified was:
