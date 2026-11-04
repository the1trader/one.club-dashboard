# one.club Execution Terminal & Institutional Trading Engine

> **Systematic ICT/SMC Intraday Execution Playbook for US100 (NQ) & US500 (ES).**  
> Features real-time multi-pair correlation, SMT divergence detection, dynamic 1% risk management, and automated 3-phase journaling.

---

## 0. MANDATORY RULE #1: TRADER AGENT ETHICAL & EXECUTION MANDATE (NON-NEGOTIABLE)

1. **ZERO FABRICATION POLICY (DATA INTEGRITY)**:
   - The trader agent **CAN NEVER** make up PnL, win rates, or trade results under any circumstances.
   - Live P&L is mathematically strictly bound: `pnl = points * multiplier * contracts`. Negative points mathematically cannot show positive dollars.
2. **STRICT PERMISSION BOUNDARY**:
   - The trader agent can **ONLY** take trades, open orders, modify protective stops, and close orders. **Nothing more than that.**
3. **COMPLETE SEPARATION: LIVE TRADES VS. HISTORICAL STUDIES**:
   - **Live Real-Time Executions**: Only trades that the agent actually took on the live tape are recorded in the live ledger and affect the account balance.
   - **Historical Chart Studies**: Theoretical chart scenarios (e.g. from TradingView screenshots) are quarantined in separate tables and logbooks with **$0.00 live balance impact**.
4. **MANDATORY REAL-TIME TRADING JOURNAL (THE 3 PHASES)**:
   - **Phase 1 (Pre-Entry)**: Full Pre-Trade Thesis (market context, SMT divergence check, 1m MSS + FVG confirmation, invalidation, R:R).
   - **Phase 2 (In-Trade)**: Real-time tape management logs (price reactions, trailing stop to breakeven at +1.5R).
   - **Phase 3 (Post-Exit)**: Post-trade retrospective (execution grade, what went well, what to improve, key lesson).
5. **NO DISAPPEARING TRADES**:
   - Every closed trade leaves an immutable, permanent audit trail showing Entry, Exit, Points, Dollar P&L, Status, and Reason.

---

## 🏛️ Database Architecture & Storage

The system features a **dual-engine database architecture**:
- **Production Cloud**: Neon PostgreSQL (Schema: `one_club`).
- **Local Embedded**: SQLite (`storage.sqlite`) zero-config fallback.

### Database Tables:

| Table | Description | Zero-Fabrication Rule |
|---|---|---|
| `one_club.live_trades` | Real tape trades executed in real time by the agent (`LIVE-001`, `LIVE-002`, `LIVE-003`). | Only real orders; updates account equity. |
| `one_club.historical_studies` | Quarantined retrospective chart studies (`STUDY-001`, `STUDY-002`, `STUDY-003`). | **$0.00 impact on live account balance.** |
| `one_club.journal_entries` | Full 3-phase write-ups with JSON pre-trade thesis, in-trade logs, and post-trade reviews. | Immutable tape logs. |
| `one_club.account_metrics` | Current account balance, equity, win rate, and profit factor. | Strictly derived from `live_trades`. |
| `one_club.agent_decisions` | Real-time decision stream and tape observations every minute. | Full audit trail of agent reasoning. |

---

## 📊 Audited Performance: Live vs. Historical

### 🔴 Real Live Executions Ledger (Real Account)
- **Starting Demo Balance:** `$50,000.00`
- **Realized Live Net P&L:** `-$540.00 (-1.08%)`
- **Real Live Account Balance:** **`$49,460.00`**
- **Live Win Rate:** `66.7%` (2 Breakeven scratch wins / 1 loss)

| Trade ID | Date & Entry Time | Exit Time | Side | Entry Price | Exit Price | Points | Realized P&L | Reason |
|---|---|---|---|---|---|---|---|---|
| **`LIVE-001`** | `2026-11-03 12:24:33 EST` | `12:49:47 EST` | SHORT | `28,242.4` | `28,241.4` | `+1.0 pt` | **`+$40.00`** | `STOP_LOSS_HIT` (BE Lock) |
| **`LIVE-002`** | `2026-11-03 12:49:47 EST` | `13:07:41 EST` | SHORT | `28,244.1` | `28,274.1` | `-30.0 pts` | **`-$600.00`** | `STOP_LOSS_HIT` (SL Hit) |
| **`LIVE-003`** | `2026-11-03 13:13:14 EST` | `13:33:29 EST` | SHORT | `28,286.9` | `28,285.9` | `+1.0 pt` | **`+$20.00`** | `STOP_LOSS_HIT` (BE Lock) |

---

### 📚 Quarantined Historical Chart Studies (Research Only)
- **Live Balance Impact:** **`$0.00` (Zero P&L added to account)**

| Study ID | Reference | Date | Session Window | Theoretical Move | Theoretical R:R | Status |
|---|---|---|---|---|---|---|
| **`STUDY-001`** | User Photo 2 | `2026-10-30` | `09:30–10:30 Cash Open` | `+205.0 pts` | `8.2R` | Non-Executed Chart Study |
| **`STUDY-002`** | User Photo 1 | `2026-11-02` | `09:30–10:30 Cash Open` | `+200.0 pts` | `4.4R` | Non-Executed Chart Study |
| **`STUDY-003`** | Photo 1 Rev | `2026-11-02` | `10:30+ Macro Delivery` | `+285.0 pts` | `5.7R` | Non-Executed Chart Study |

---

## ⚡ Institutional Time Windows & Strategy Logic

1. **Window 1: 07:30 – 08:30 EST (Pre-Market Range Definition)**
   - Establishes baseline range: $H_{730}$, $L_{730}$, and Equilibrium ($Eq_{730}$).
   - Agent stands **FLAT**.

2. **Window 2: 08:30 – 09:30 EST (Manipulation & Liquidity Purge)**
   - Identifies if 08:30 sweeps high/low or coils (Type A expansion vs Type B compression).
   - If compressed without purge $\rightarrow$ delayed energy trap at cash open.

3. **Window 3: 09:30 – 10:30 EST (Cash Open Execution)**
   - **09:30 Correlation Gate**: If NQ & ES diverge (one green, one red), agent locks in standby to avoid the opening trap.
   - If in-sync, takes structural continuation dip.

4. **Window 4: 10:15 – 10:30+ EST (Macro SMT Reversal Delivery)**
   - Screens for Bearish/Bullish SMT Divergence (ES prints new high while NQ forms lower high, or vice versa).
   - Confirms entry via 1m Market Structure Shift (MSS) + Fair Value Gap (FVG) retest.

---

## 🚀 Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env to set your Neon PostgreSQL DATABASE_URL (or leave empty for SQLite)
```

### 2. Synchronize Database
```bash
python3 scripts/sync_db.py
```

### 3. Launch Execution Terminal
```bash
python3 server.py
# Open http://localhost:8899 in your browser
```

---

## 📁 Repository Structure

```
one.club-dashboard/
├── index.html                   # Institutional Live Execution Terminal
├── server.py                    # Lightweight Python backend server & API
├── app/
│   ├── db.py                    # Neon PostgreSQL + SQLite dual-engine DB adapter
│   ├── schema.sql               # PostgreSQL (one_club) & SQLite schema DDL
│   ├── agent.py                 # Time & Price Decision Engine
│   ├── paper_account.py         # Dynamic 1% risk paper trading engine
│   └── journal.py               # 3-Phase real-time trading journal system
├── scripts/
│   ├── sync_db.py               # Database sync runner
│   ├── audit_inspector.py       # Bar-by-bar chronological backtest auditor
│   ├── study_60d_sessions.py    # 60-day historical session analytics
│   └── start_terminal.sh        # One-click startup script
├── memory/
│   ├── historical_case_studies.json # Quarantined chart studies
│   ├── statistical_insights.json    # Audited 60-day NYSE session analytics
│   └── session_learnings.json       # Live pattern match fingerprints
├── logs/
│   ├── paper_account.json       # Real live tape account state ($49,460.00)
│   ├── trade_journal.json       # Real live trade journal (LIVE-001, LIVE-002, LIVE-003)
│   └── dashboard_data.json      # Live polling stream
└── journal/
    ├── TRADE_LOGBOOK.md         # Immutable Live Trade Logbook
    └── HISTORICAL_CASE_STUDIES.md # Separated Historical Studies Logbook
```
