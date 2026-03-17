# Backtest Workflow — Quant Trading Research

This document defines the standard process for conducting, structuring, and publishing strategy backtests in this repository.

The goal is to ensure that all research is:
- reproducible
- structured
- comparable across projects
- clearly communicated

---

## 1. Architecture Overview

All research is split into two environments:

### A. Working Research Environment (private / local)
Used for:
- notebooks
- experimentation
- parameter sweeps
- debugging
- raw exports

Example:

C:\Users\olivi\lvn-auction-backtester


### B. Public Research Repository (this repo)
Used for:
- structured summaries
- validated results
- visualizations
- conclusions

---

## 2. Project Placement

All full strategy tests must be placed under:


projects/strategy_backtesting/


Each backtest gets its own folder:


projects/strategy_backtesting/<project_name>/


### Naming Convention

Use descriptive names:

- `lvn_auction_friction_review`
- `liquidity_sweep_reversal_test`
- `bos_retest_execution_model`

Avoid:
- `final_v2`
- `test_fixed`
- `notebook7`

---

## 3. Standard Project Structure

Each project must follow this structure:


<project_name>/
README.md
methodology.md
findings.md
results/
figures/


---

## 4. File Definitions

### README.md
High-level overview:
- strategy idea
- goal of research
- key result
- conclusion
- status

---

### methodology.md
Details how the research was conducted:
- system architecture
- datasets
- parameters tested
- research stages
- evaluation metrics
- limitations

---

### findings.md
Core output of the research:
- what worked
- what failed
- best configurations
- robustness results
- friction sensitivity (if applicable)
- final conclusion
- next steps

---

### results/
Contains only clean, relevant outputs:
- CSV summaries
- candidate comparisons
- friction results
- evaluation tables

Do NOT include:
- raw debug data
- intermediate junk outputs

---

### figures/
Contains visual summaries:
- performance charts
- friction curves
- candidate comparisons

All figures must be reproducible from scripts.

---

## 5. Research Process

### Step 1 — Conduct research (working repo)
Perform:
- backtesting
- parameter sweeps
- robustness testing
- friction modeling

---

### Step 2 — Define conclusion

Before publishing, clearly answer:

1. What was tested?
2. What worked?
3. What failed?
4. What is the final conclusion?
5. Is it production-ready?

---

### Step 3 — Create project in public repo


projects/strategy_backtesting/<project_name>/


---

### Step 4 — Write documentation

Create:
- README.md
- methodology.md
- findings.md

---

### Step 5 — Export results

Copy only clean outputs from working repo:

Example:

lvn-auction-backtester/friction_results/*.csv
→ results/


---

### Step 6 — Generate figures

Use a reproducible script:


scripts/generate_<project>_figures.py


Output:


figures/*.png


---

### Step 7 — Add visuals to README

Example:

```markdown
## Key Visuals

![Chart](figures/example.png)