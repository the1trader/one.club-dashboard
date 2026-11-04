# 1trade Historical Chart Studies & Retrospective Case Studies
**Purpose:** Research & Backtested Scenarios from Uploaded Charts (Non-Executed)
**Live Account Impact:** **$0.00** (Zero balance impact. No simulated dollars added to the live account.)

---

## 📚 Overview of Case Studies

These historical scenarios were analyzed from the chart screenshots uploaded by the trader to reverse-engineer ICT Time & Price delivery. Because they were not executed live on the tape by the autonomous agent, they are strictly quarantined here as educational benchmarks and backtests.

---

## [STUDY-001] 2026-10-30 — Scenario 2: 08:30 Compression → 09:30 Judas Sweep Reversal
- **Reference:** User Photo 2 (US 100 Cash CFD 1m / 5m)
- **Time Window:** Window 3 (09:30–10:30 AM EST Cash Open)
- **Side:** 🟢 LONG (Hypothetical)
- **Theoretical Entry:** `28,485.0` (09:42 EST)
- **Theoretical Exit:** `28,690.0` (10:18 EST)
- **Theoretical Points Captured:** `+205.0 pts`
- **Theoretical Risk-to-Reward:** `8.2R`
- **Execution Type:** ⚠️ **NON-EXECUTED HISTORICAL BACKTEST**
- **Live Account Impact:** `$0.00`
- **Key Mechanics:** 
  07:30 range formed between 28,630 (Low) and 28,690 (High). 08:30 stayed compressed inside. 09:30 cash open engineered a Judas Swing dump below the 07:30 low, sweeping sell-side liquidity before violently reversing into full buy-side delivery of the 07:30 high (+205 pts).

---

## [STUDY-002] 2026-11-02 — Scenario 1: 08:30 Sweep & Surge → 09:30 Dip Continuation
- **Reference:** User Photo 1 (US 100 Cash CFD 1m)
- **Time Window:** Window 3 (09:30–10:30 AM EST Cash Open)
- **Side:** 🟢 LONG (Hypothetical)
- **Theoretical Entry:** `28,540.0` (09:48 EST)
- **Theoretical Exit:** `28,740.0` (10:28 EST)
- **Theoretical Points Captured:** `+200.0 pts`
- **Theoretical Risk-to-Reward:** `4.4R`
- **Execution Type:** ⚠️ **NON-EXECUTED HISTORICAL BACKTEST**
- **Live Account Impact:** `$0.00`
- **Key Mechanics:**
  08:30 swept 07:30 low and surged upward. 09:30 cash open pulled back into discount Fair Value Gap, providing an ideal buy continuation before expanding +200 pts into the 10:30 peak.

---

## [STUDY-003] 2026-11-02 — Scenario 1 Reversal: 10:30 Macro High Sweep Short
- **Reference:** User Photo 1 Reversal
- **Time Window:** Window 4 (10:30+ AM EST Macro Delivery)
- **Side:** 🔴 SHORT (Hypothetical)
- **Theoretical Entry:** `28,705.0` (10:30 EST)
- **Theoretical Exit:** `28,420.0` (11:15 EST)
- **Theoretical Points Captured:** `+285.0 pts`
- **Theoretical Risk-to-Reward:** `5.7R`
- **Execution Type:** ⚠️ **NON-EXECUTED HISTORICAL BACKTEST**
- **Live Account Impact:** `$0.00`
- **Key Mechanics:**
  After running up +320 pts into 10:30, buy-side liquidity was fully delivered into HTF resistance. A 1m Bearish Market Structure Shift confirmed the exhaustion, leading to a -285 pt markdown back into discount.

---

## 🔬 60-Day Historical Inspector Audit Summary
- **Dataset:** 50 NYSE sessions (60 calendar days).
- **Audited Raw Strategy Performance:** 6 Wins / 3 Breakeven / 29 Losses (**15.8% Win Rate** / -366 pts / -$7,320 Net).
- **Core Finding:** 23 out of 29 losses failed on the 09:30 cash open bar because tight pre-market stop losses (2–4 pts) were liquidated by opening volatility.
- **Audited Calibrations:** Stop losses must be structurally anchored (20–40 pts), and cash open entries must wait for the 09:30–10:00 Judas sweep or 10:15 SMT divergence confirmation.
