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

va_containment_threshold = 0.60
min_lvn_height_pct = 10
min_edge_bps = 30
min_rejection_wick_ratio = 0.0


Performance:

- Trades: 107  
- Profit Factor: 4.09  
- Avg PnL per trade: 69.13  
- Total PnL: 7396.57  
- First-half PF: 4.84  
- Second-half PF: 3.75  

At this stage, the system appeared highly promising.

---

## 4. Negative Findings

### 4.1 Wick-Based Rejection Filtering Was Ineffective

Adding minimum wick-ratio constraints:

- reduced trade count
- degraded profit factor
- introduced instability

Conclusion:

> Wick-based filtering does not contribute to the core edge in this framework.

---

### 4.2 High Dependence on Stop-Based Exits

A large portion of trades exited via rejection stops (`sl_rej`), indicating:

- frequent invalidation of entry assumptions
- high sensitivity to entry precision

This became critical under friction.

---

## 5. Friction Sensitivity — Critical Result

A dedicated friction analysis was performed using:

- trading fees
- execution slippage assumptions

### Aggregate Results

| Scenario | PF | Avg PnL |
|--------|----|--------|
| No friction | 4.18 | 68.0 |
| Low friction | 1.77 | 29.3 |
| Medium friction | 1.30 | 13.8 |
| High friction | 0.64 | -25.0 |

### Interpretation

- The strategy **loses most of its edge under realistic conditions**
- Under moderate friction, performance drops below acceptable thresholds
- Under pessimistic assumptions, the system becomes **unprofitable**

---

## 6. Candidate Comparison Under Friction

All serious candidates failed to remain profitable under friction:

| Candidate | PF (friction) | Avg PnL |
|----------|--------------|--------|
| 0.60 / 10 / 30 | 0.60 | -28.9 |
| 0.60 / 10 / 35 | 0.66 | -23.4 |
| 0.60 / 15 / 35 | 0.70 | -20.8 |
| 0.65 / 15 / 20 | 0.62 | -25.1 |
| 0.65 / 10 / 35 | 0.63 | -26.1 |

No configuration maintained profitability.

---

## 7. Exit Distribution Analysis

| Exit Type | Trades | Avg PnL |
|----------|------|--------|
| tp_poc | 88 | +115.2 |
| time_stop | 21 | +152.0 |
| sl_rej | 303 | -78.0 |

### Key Insight

- The system relies on **fewer large winners**
- but suffers from **many frequent losses**
- friction increases losses and compresses winners

This leads to **edge collapse under realistic execution conditions**

---

## 8. Core Conclusion

> The LVN → POC concept is structurally valid, but the current implementation lacks sufficient edge margin to survive realistic execution friction.

Specifically:

- strong performance under ideal conditions
- insufficient robustness under real-world assumptions
- excessive reliance on precise entries and low-cost execution

---

## 9. Practical Outcome

Although the standalone strategy is not suitable for live deployment in its current form, the research produced valuable insights:

- value-area containment is a meaningful contextual filter
- LVN significance is relevant but insufficient alone
- execution sensitivity must be explicitly modeled in strategy design

These insights are now being transferred into:

> **Telegram-based alert systems as contextual filters rather than standalone trade signals**

---

## 10. Status

**Status: Completed (Not production-ready)**

This research is considered complete.  
Further work will focus on integrating validated components into broader executio