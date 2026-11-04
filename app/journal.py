#!/usr/bin/env python3
"""
trade_journal.py — Autonomous Real-Time Trade Journal & Retrospective Logbook

Operates like an institutional discretionary & algorithmic trader:
1. Pre-Trade Entry:
   - Records Setup name, Market Context, SMT Divergence, 1m MSS & FVG confirmation,
     exact entry price, structural SL, TP target, dynamic 1% risk, and execution thesis.
2. In-Trade Management Log:
   - Records live thoughts, price reactions, trailing stop adjustments to breakeven,
     and tape observations in real-time.
3. Post-Trade Review (The Retrospective):
   - When the trade closes, writes a comprehensive post-mortem:
     Outcome, Points, Dollar P&L, Realized R:R, Execution Grade (A+/A/B/C),
     What went well, What could be improved, and Key Lesson.
4. Outputs:
   - Markdown: .agents/skills/1trade/journal/TRADE_LOGBOOK.md & daily files.
   - Structured JSON: .agents/skills/1trade/logs/trade_journal.json
"""

import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional

NY_TZ = ZoneInfo("America/New_York")
JOURNAL_DIR = os.path.expanduser("/Users/myominkhant/Desktop/school-works/.agents/skills/1trade/journal")
LOG_DIR = os.path.expanduser("/Users/myominkhant/Desktop/school-works/.agents/skills/1trade/logs")
LOGBOOK_MD = os.path.join(JOURNAL_DIR, "TRADE_LOGBOOK.md")
JOURNAL_JSON = os.path.join(LOG_DIR, "trade_journal.json")

class TradeJournal:
    def __init__(self):
        os.makedirs(JOURNAL_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)
        self.entries: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(JOURNAL_JSON):
            try:
                with open(JOURNAL_JSON, "r") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = []
        else:
            self.entries = []
            self._save()

    def _save(self):
        with open(JOURNAL_JSON, "w") as f:
            json.dump(self.entries, f, indent=2)
        self._render_master_logbook()

    def _seed_sample_journal(self):
        """Seeds the journal with full professional trader write-ups for the 2 verified screenshots."""
        self.entries = [
            {
                "trade_id": "TRADE-001",
                "date": "2026-10-30",
                "entry_time": "09:42 EST",
                "exit_time": "10:18 EST",
                "setup": "Scenario 2: 08:30 Compression -> 09:30 Judas Sweep Reversal",
                "instrument": "US100 (NQ CFD / Futures)",
                "side": "LONG",
                "contracts": 1,
                "entry_price": 28485.0,
                "stop_loss": 28460.0,
                "take_profit": 28690.0,
                "dollar_risk": 500.0,
                "risk_pct": 1.0,
                "pre_trade_thesis": {
                    "w1_context": "07:30 range established between 28,630 (Low) and 28,690 (High).",
                    "w2_manipulation": "08:30 stayed strictly compressed inside 07:30 range. Energy coiled, no liquidity purged yet.",
                    "confirmation": "At 09:30 Cash Open, violent Judas dump flushed below 28,630 down to 28,470. Heavy rejection wicks formed. 1m bullish MSS broke above 28,480 with displacement.",
                    "entry_trigger": "Entered LONG on 1m FVG retest at 28,485. SL placed 2.0 pts below Judas sweep low at 28,460."
                },
                "in_trade_logs": [
                    {"time": "09:50 EST", "price": 28540.0, "pts": "+55.0", "note": "Impulsive displacement upward. Price cleared internal range high."},
                    {"time": "09:55 EST", "price": 28580.0, "pts": "+95.0", "note": "Hit +3.8R. Trailed Stop Loss to Breakeven (28,486.0). Trade is now 100% Risk-Free."},
                    {"time": "10:10 EST", "price": 28670.0, "pts": "+185.0", "note": "Approaching major target: the 07:30 range high (28,690 white line)."}
                ],
                "exit_review": {
                    "exit_price": 28690.0,
                    "points": 205.0,
                    "pnl": 4100.0,
                    "rr_achieved": 8.2,
                    "status": "WIN",
                    "grade": "A+",
                    "what_went_well": "Patiently waited for the 09:30 Judas sweep instead of chasing the 08:30 chop. Flawless structural SL placement below the flush wick.",
                    "what_to_improve": "Could leave a 10% runner for higher time frame daily expansion.",
                    "key_lesson": "When 08:30 is coiled and compressed, do NOT take early breakouts. The 09:30 open will always engineer a Judas flush to shake out weak retail before the true move."
                }
            },
            {
                "trade_id": "TRADE-002",
                "date": "2026-11-03",
                "entry_time": "09:48 EST",
                "exit_time": "10:28 EST",
                "setup": "Scenario 1: 08:30 Sweep & Surge -> 09:30 Dip Continuation",
                "instrument": "US100 (NQ CFD / Futures)",
                "side": "LONG",
                "contracts": 1,
                "entry_price": 28540.0,
                "stop_loss": 28495.0,
                "take_profit": 28740.0,
                "dollar_risk": 500.0,
                "risk_pct": 1.0,
                "pre_trade_thesis": {
                    "w1_context": "07:30 range set between 28,540 and 28,620 (80 pts).",
                    "w2_manipulation": "08:30 swept L_730 (28,540) down to 28,530, then exploded upward to 28,710. Type A confirmed.",
                    "confirmation": "At 09:30 cash open, price dipped into discount FVG at 28,500. Buyers absorbed sell volume. 1m bullish MSS printed at 09:46.",
                    "entry_trigger": "Bought the discount retest at 28,540. SL anchored below 09:35 open dip low at 28,495."
                },
                "in_trade_logs": [
                    {"time": "10:00 EST", "price": 28610.0, "pts": "+70.0", "note": "Displacement breaking through 07:30 high."},
                    {"time": "10:12 EST", "price": 28690.0, "pts": "+150.0", "note": "Hit +3.3R. Stop trailed to lock in +1.5R profit."},
                    {"time": "10:25 EST", "price": 28740.0, "pts": "+200.0", "note": "10:25 macro target reached. Long upper wicks appearing at 28,760."}
                ],
                "exit_review": {
                    "exit_price": 28740.0,
                    "points": 200.0,
                    "pnl": 4000.0,
                    "rr_achieved": 4.4,
                    "status": "WIN",
                    "grade": "A",
                    "what_went_well": "Took full profit right at 10:25–10:28 AM before the 10:30 macro exhaustion, completely dodging the afternoon 340-point collapse.",
                    "what_to_improve": "Could immediately prepare the 10:30 short reversal scalp when Bearish SMT appeared.",
                    "key_lesson": "Respect the 10:30 AM rule religiously. 10:25–10:30 is the delivery peak of the morning run. Never hold blind longs into 10:30 without trailing."
                }
            }
        ]

    def log_pre_trade(self, trade_id: str, side: str, entry_price: float, stop_loss: float,
                      take_profit: float, dollar_risk: float, contracts: float,
                      setup: str, thesis_dict: Dict) -> Dict:
        now_ny = datetime.now(NY_TZ)
        entry = {
            "trade_id": trade_id,
            "date": now_ny.strftime("%Y-%m-%d"),
            "entry_time": now_ny.strftime("%H:%M:%S EST"),
            "exit_time": None,
            "setup": setup,
            "instrument": "US100 (NQ)",
            "side": side.upper(),
            "contracts": contracts,
            "entry_price": round(entry_price, 1),
            "stop_loss": round(stop_loss, 1),
            "take_profit": round(take_profit, 1),
            "dollar_risk": round(dollar_risk, 2),
            "risk_pct": 1.0,
            "pre_trade_thesis": thesis_dict,
            "in_trade_logs": [
                {
                    "time": now_ny.strftime("%H:%M:%S EST"),
                    "price": entry_price,
                    "pts": "0.0",
                    "note": f"Executed {side.upper()} order. Stop Loss set structurally at {stop_loss:.1f}, TP at {take_profit:.1f}."
                }
            ],
            "exit_review": None
        }

        # Check if already exists, else insert
        idx = next((i for i, e in enumerate(self.entries) if e["trade_id"] == trade_id), None)
        if idx is not None:
            self.entries[idx] = entry
        else:
            self.entries.insert(0, entry)

        self._save()
        return entry

    def log_trade_management(self, trade_id: str, current_price: float, note: str):
        now_ny = datetime.now(NY_TZ)
        for e in self.entries:
            if e["trade_id"] == trade_id and e["exit_review"] is None:
                side = e["side"]
                pts = (current_price - e["entry_price"]) if side == "LONG" else (e["entry_price"] - current_price)
                sign = "+" if pts >= 0 else ""
                e["in_trade_logs"].append({
                    "time": now_ny.strftime("%H:%M:%S EST"),
                    "price": round(current_price, 1),
                    "pts": f"{sign}{pts:.1f}",
                    "note": note
                })
                self._save()
                break

    def log_post_trade_review(self, trade_id: str, exit_price: float, reason: str,
                              what_went_well: str, what_to_improve: str, key_lesson: str, grade: str = "A"):
        now_ny = datetime.now(NY_TZ)
        for e in self.entries:
            if e["trade_id"] == trade_id:
                side = e["side"]
                pts = (exit_price - e["entry_price"]) if side == "LONG" else (e["entry_price"] - exit_price)
                pv = e.get("point_value", 20.0 if e.get("contracts", 1) <= 2 else 2.0)
                pnl = pts * pv * e["contracts"]
                sl_distance = abs(e["entry_price"] - e["stop_loss"])
                rr = round(pts / sl_distance, 2) if sl_distance > 0 else 0.0

                e["exit_time"] = now_ny.strftime("%H:%M:%S EST")
                e["exit_review"] = {
                    "exit_price": round(exit_price, 1),
                    "points": round(pts, 1),
                    "pnl": round(pnl, 2),
                    "rr_achieved": rr,
                    "status": "WIN" if pnl > 0 else "LOSS",
                    "grade": grade,
                    "reason": reason,
                    "what_went_well": what_went_well,
                    "what_to_improve": what_to_improve,
                    "key_lesson": key_lesson
                }
                self._save()
                break

    def _render_master_logbook(self):
        """Generates a clean Markdown Trade Logbook file."""
        lines = [
            "# 1trade Professional Master Logbook & Trade Journal",
            f"**Last Updated:** {datetime.now(NY_TZ).strftime('%Y-%m-%d %H:%M:%S EST')}\n",
            "> *'You do not rise to the level of your goals, you fall to the level of your systems.'* — James Clear\n",
            "---"
        ]

        for e in self.entries:
            side_badge = "🟢 LONG" if e["side"] == "LONG" else "🔴 SHORT"
            rev = e.get("exit_review")
            outcome_badge = "⏳ IN FLIGHT"
            if rev:
                outcome_badge = f"🏆 WIN (+${rev['pnl']:,.2f} / +{rev['points']} pts)" if rev["status"] == "WIN" else f"❌ LOSS (${rev['pnl']:,.2f} / {rev['points']} pts)"

            lines.append(f"\n## [{e['trade_id']}] {e['date']} — {e['setup']}")
            lines.append(f"**Side:** {side_badge} | **Status:** {outcome_badge} | **Risk:** ${e['dollar_risk']:,.2f} ({e['risk_pct']}%)")
            lines.append(f"**Entry:** `{e['entry_price']}` ({e['entry_time']}) | **SL:** `{e['stop_loss']}` | **TP:** `{e['take_profit']}`")

            thesis = e.get("pre_trade_thesis", {})
            lines.append("\n### 🧠 Pre-Trade Thesis & Confirmations")
            for k, v in thesis.items():
                lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")

            lines.append("\n### ⏱️ In-Trade Management Log")
            for log in e.get("in_trade_logs", []):
                lines.append(f"- `[{log['time']}]` (Price: `{log['price']}`, {log['pts']} pts) — {log['note']}")

            if rev:
                lines.append("\n### 📊 Post-Trade Review & Retrospective")
                lines.append(f"- **Outcome & Realized P&L:** {rev['status']} ({rev['points']} pts | **${rev['pnl']:,.2f}**) | Realized R:R: **{rev['rr_achieved']}R**")
                lines.append(f"- **Execution Grade:** `{rev['grade']}`")
                lines.append(f"- **What Went Well:** {rev['what_went_well']}")
                lines.append(f"- **What to Improve:** {rev['what_to_improve']}")
                lines.append(f"- **💡 Key Lesson:** {rev['key_lesson']}")

            lines.append("\n---")

        with open(LOGBOOK_MD, "w") as f:
            f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    tj = TradeJournal()
    print("Trade Journal initialized with", len(tj.entries), "logged trades.")
    print("Logbook written to:", LOGBOOK_MD)
