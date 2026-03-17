# Methodology — LVN Auction Backtest

## 1. Objective

The goal of this research was to evaluate whether reactions from Low Volume Nodes (LVNs) toward the developing Point of Control (POC) can produce a robust trading edge.

---

## 2. System Architecture

The strategy uses a dual-timeframe approach:

- **1H timeframe**
  - Session-anchored volume profile
  - LVN detection
  - Value Area (VAH / VAL)
  - Developing POC
  - Value-area containment filter

- **15m timeframe**
  - Entry timing
  - Rejection detection
  - Stop placement
  - Exit execution

---

## 3. Core Parameters

Key parameters explored:

- `va_containment_threshold`
- `min_lvn_height_pct`
- `min_edge_bps`
- `min_rejection_wick_ratio`
- `tp_target = poc`
- `max_hold_bars_15m`

---

## 4. Research Process

The research progressed through several stages:

1. Baseline backtest (single configuration)
2. Contextual filtering (value-area containment)
3. Wick-based rejection testing
4. Parameter sweep across multiple configurations
5. Candidate comparison
6. Friction sensitivity analysis

---

## 5. Evaluation Metrics

Performance was evaluated using:

- Profit Factor (PF)
- Average PnL per trade
- Total PnL
- Trade count
- First-half vs second-half PF
- Exit reason distribution
- Friction robustness

---

## 6. Friction Modeling

A simplified friction model was applied:

- Fee assumptions (bps)
- Slippage scenarios (low → high)
- Impact calculated relative to trade notional

Scenarios tested:

- No friction
- Low friction
- Medium friction
- High friction

---

## 7. Limitations

- 1-unit notional assumption
- Simplified slippage model
- No order book / latency modeling
- No queue position modeling

Results should therefore be interpreted as:

> **relative robustness tests, not execution-accurate forecasts**