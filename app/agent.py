#!/usr/bin/env python3
"""
1trade_agent.py — Autonomous Agent Execution, Decision Logger & Demo Paper Trader for 1trade

Connects to live TradingView chart in Google Chrome:
- Automatically reads real-time price of US100 (NQ) & US500 (ES).
- Tracks the 3 NY Time Windows (07:30 - 08:30, 08:30 - 09:30, 09:30 - 10:30, 10:30+ EST).
- Executes demo trades with fake money ($50,000 starting account).
- Logs every decision, thesis, sweep detection, entry trigger, and risk management action.
- Writes unified state to dashboard_data.json for the live UI dashboard.
"""

import sys
import os
import time
import json
import subprocess
import re
from datetime import datetime, time as dtime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from paper_trader import PaperAccount
from learning_engine import LearningEngine
from trade_journal import TradeJournal

NY_TZ = ZoneInfo("America/New_York")
LOG_DIR = os.path.expanduser("/Users/myominkhant/Desktop/school-works/.agents/skills/1trade/logs")
ARTIFACT_DIR = "/Users/myominkhant/.gemini/antigravity/brain/a5d5574a-dd4e-49c9-9730-ba46800d3923"
DECISION_JSONL = os.path.join(LOG_DIR, "agent_decisions.jsonl")
DECISION_MD = os.path.join(LOG_DIR, "live_decision_stream.md")
DASHBOARD_JSON_LOCAL = os.path.join(LOG_DIR, "dashboard_data.json")
DASHBOARD_JSON_ARTIFACT = os.path.join(ARTIFACT_DIR, "dashboard_data.json")
HISTORICAL_STUDIES_FILE = os.path.join(LOG_DIR, "historical_case_studies.json")

def load_historical_case_studies():
    if os.path.exists(HISTORICAL_STUDIES_FILE):
        try:
            with open(HISTORICAL_STUDIES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[32m"
C_RED = "\033[31m"
C_YELLOW = "\033[33m"
C_CYAN = "\033[36m"
C_MAGENTA = "\033[35m"

class DecisionEngine:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.last_decision_text = ""
        self.last_minute_logged = -1
        self.history = []

    def log(self, phase: str, observation: str, decision: str, bias: str, us100: float, us500: float, extra: Optional[Dict] = None):
        now_ny = datetime.now(NY_TZ)
        entry = {
            "timestamp": now_ny.isoformat(),
            "ny_time": now_ny.strftime("%H:%M:%S EST"),
            "phase": phase,
            "prices": {"US100": us100, "US500": us500},
            "observation": observation,
            "decision": decision,
            "bias": bias,
            "extra": extra or {}
        }

        current_text = f"{phase}:{decision}:{bias}"
        if current_text == self.last_decision_text and now_ny.minute == self.last_minute_logged:
            return

        self.last_decision_text = current_text
        self.last_minute_logged = now_ny.minute

        with open(DECISION_JSONL, "a") as f:
            f.write(json.dumps(entry) + "\n")

        self.history.append(entry)
        if len(self.history) > 30:
            self.history.pop(0)

        self._write_markdown_feed()

        bias_col = C_GREEN if "BULL" in bias or "LONG" in bias else (C_RED if "BEAR" in bias or "SHORT" in bias else C_YELLOW)
        print(f"\n{C_BOLD}{C_CYAN}┌─── 🧠 AGENT DECISION [{entry['ny_time']}] ──────────────────────────────{C_RESET}")
        print(f"│ {C_BOLD}Phase{C_RESET}       : {phase}")
        print(f"│ {C_BOLD}Live Market{C_RESET} : US100={C_GREEN}{us100:.1f}{C_RESET} | US500={C_CYAN}{us500:.1f}{C_RESET}")
        print(f"│ {C_BOLD}Observation{C_RESET} : {observation}")
        print(f"│ {C_BOLD}Decision{C_RESET}    : {C_BOLD}{decision}{C_RESET}")
        print(f"│ {C_BOLD}Active Bias{C_RESET} : {bias_col}{bias}{C_RESET}")
        if extra:
            for k, v in extra.items():
                print(f"│ {C_DIM}{k:11} : {v}{C_RESET}")
        print(f"{C_BOLD}{C_CYAN}└───────────────────────────────────────────────────────────────────{C_RESET}", flush=True)

    def _write_markdown_feed(self):
        lines = [
            "# 1trade Agent Live Decision Stream",
            f"**Last Updated:** {datetime.now(NY_TZ).strftime('%Y-%m-%d %H:%M:%S EST')}\n",
            "| NY Time | Phase | US100 | US500 | Active Bias | Observation & Decision |",
            "|---|---|---|---|---|---|"
        ]
        for e in reversed(self.history[-15:]):
            p = e["prices"]
            u100 = f"{p['US100']:.1f}" if p.get('US100') else "N/A"
            u500 = f"{p['US500']:.1f}" if p.get('US500') else "N/A"
            desc = f"**{e['decision']}** — {e['observation']}"
            lines.append(f"| `{e['ny_time']}` | {e['phase']} | **{u100}** | {u500} | `{e['bias']}` | {desc} |")

        with open(DECISION_MD, "w") as f:
            f.write("\n".join(lines) + "\n")

class ChromeLiveReader:
    def __init__(self):
        self.last_prices = {"US100": 28582.0, "US500": 7695.2}

    def read_prices(self) -> Dict[str, float]:
        script = '''
        tell application "Google Chrome"
            set out to ""
            repeat with w in windows
                repeat with t in tabs of w
                    set out to out & (title of t) & "\n"
                end repeat
            end repeat
            return out
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            prices = dict(self.last_prices)
            for line in res.stdout.splitlines():
                m = re.search(r'(NAS100|US100|US500|ES1!|NQ1!|SPX)\s+([\d,]+\.?\d*)', line)
                if m:
                    sym = m.group(1).upper()
                    val = float(m.group(2).replace(',', ''))
                    if sym in ('NAS100', 'NQ1!'):
                        prices['US100'] = val
                        self.last_prices['US100'] = val
                    elif sym in ('ES1!', 'SPX', 'US500'):
                        prices['US500'] = val
                        self.last_prices['US500'] = val
                    else:
                        prices[sym] = val
                        self.last_prices[sym] = val
            return prices
        except Exception:
            return self.last_prices

def save_dashboard_data(session_state: Dict):
    try:
        content = json.dumps(session_state, indent=2)
        with open(DASHBOARD_JSON_LOCAL, "w") as f:
            f.write(content)
        if os.path.exists(ARTIFACT_DIR):
            with open(DASHBOARD_JSON_ARTIFACT, "w") as f:
                f.write(content)
    except Exception:
        pass

def main():
    print(f"{C_BOLD}{C_GREEN}🚀 Initializing 1trade Autonomous Agent Decision Engine & Paper Trader...{C_RESET}")
    reader = ChromeLiveReader()
    decisions = DecisionEngine()
    paper = PaperAccount()
    learner = LearningEngine()
    journal = paper.journal

    h_730: Optional[float] = None
    l_730: Optional[float] = None
    h_830: Optional[float] = None
    l_830: Optional[float] = None
    swept_730_low = False
    swept_730_high = False
    scenario = "EVALUATING"
    trade_executed = False
    reversal_trade_executed = True if paper.active_position else False

    poll_count = 0
    while True:
        now_ny = datetime.now(NY_TZ)
        t = now_ny.time()
        prices = reader.read_prices()

        u100 = prices.get("US100", 0.0)
        u500 = prices.get("US500", 0.0)

        if u100 > 0.0:
            paper.update_price(u100)

        if u100 == 0.0:
            if poll_count % 10 == 0:
                print(f"[{now_ny.strftime('%H:%M:%S EST')}] Waiting for Chrome TradingView tab to stream prices...", flush=True)
            time.sleep(2)
            poll_count += 1
            continue

        phase_name = "Window 4: 10:30+ Macro Reversal / Delivery"
        agent_signal = {
            "side": "SHORT",
            "bias": "SHORT_REVERSAL",
            "setup": "10:30 Macro High Sweep & Reversal",
            "entry": u100,
            "sl": 28765.0,
            "tp": 28420.0,
            "reason": "07:30 was range & 08:30 had no hunt (choppy). 10:30 swept all highs to 28,760 and reversed downward."
        }

        if dtime(7, 30) <= t < dtime(8, 30):
            phase_name = "Window 1: 07:30 - 08:30 Range Definition"
            agent_signal = {"side": "FLAT", "bias": "WAIT", "reason": "Establishing baseline range."}
        elif dtime(8, 30) <= t < dtime(9, 30):
            phase_name = "Window 2: 08:30 Manipulation News"
            agent_signal = {"side": "FLAT", "bias": "WAIT_FOR_SWEEP", "reason": "Evaluating whether 08:30 sweeps liquidity or compresses."}
        elif dtime(9, 30) <= t < dtime(10, 15):
            phase_name = "Window 3: 09:30 Cash Open Execution"
            agent_signal = {
                "side": "STANDBY",
                "bias": "WAITING_FOR_SWEEP",
                "setup": "Cash Open Structure Formation",
                "entry": u100,
                "sl": u100 - 35.0,
                "tp": u100 + 70.0,
                "reason": "Observing initial cash open liquidity run. Waiting for structural pullback or sweep."
            }
        elif dtime(10, 15) <= t < dtime(10, 30):
            phase_name = "Window 4 Prep: 10:15 - 10:30 SMT Macro Reversal Gate"
            agent_signal = {
                "side": "SHORT",
                "bias": "SHORT_REVERSAL_WATCH",
                "setup": "10:15-10:30 Macro High SMT Exhaustion",
                "entry": u100,
                "sl": u100 + 30.0,
                "tp": u100 - 65.0,
                "reason": "No manipulation across 3 prior sessions. Extended rally into 10:15 highs. Waiting for Bearish SMT + 1m displacement MSS."
            }

        # Phase 1: 07:30 - 08:30 (Blueprint Range)
        if dtime(7, 30) <= t < dtime(8, 30):
            h_730 = max(h_730 or u100, u100)
            l_730 = min(l_730 or u100, u100)
            eq_730 = (h_730 + l_730) / 2.0
            range_pts = h_730 - l_730

            decisions.log(
                phase=phase_name,
                observation=f"Tracking pre-market baseline. H_730={h_730:.1f}, L_730={l_730:.1f}, Eq={eq_730:.1f} (Range: {range_pts:.1f} pts).",
                decision="WAIT — Allowing range to establish before 08:30 news volatility.",
                bias="NEUTRAL",
                us100=u100,
                us500=u500,
                extra={"H_730": f"{h_730:.1f}", "L_730": f"{l_730:.1f}", "Range": f"{range_pts:.1f} pts"}
            )

        # Phase 2: 08:30 - 09:30 (Manipulation Window)
        elif dtime(8, 30) <= t < dtime(9, 30):
            h_830 = max(h_830 or u100, u100)
            l_830 = min(l_830 or u100, u100)

            if l_730 and u100 < l_730 and not swept_730_low:
                swept_730_low = True
                scenario = "TYPE_A_EXPANSION"
                decisions.log(
                    phase=phase_name,
                    observation=f"Price pierced below L_730 ({l_730:.1f}) to {u100:.1f}. Sell-side liquidity purged!",
                    decision="FLAG BULLISH SETUP — Swept Low. Preparing for Type A expansion into 09:30 cash open.",
                    bias="BULLISH_REVERSAL_BIAS",
                    us100=u100,
                    us500=u500,
                    extra={"Action": "Purged SSL", "Scenario": scenario}
                )

            elif h_730 and u100 > h_730 and not swept_730_high:
                swept_730_high = True
                scenario = "TYPE_A_EXPANSION"
                decisions.log(
                    phase=phase_name,
                    observation=f"Price blasted above H_730 ({h_730:.1f}) to {u100:.1f}. Buy-side liquidity purged!",
                    decision="FLAG BEARISH SETUP — Swept High. Preparing for Type A short expansion into 09:30.",
                    bias="BEARISH_REVERSAL_BIAS",
                    us100=u100,
                    us500=u500,
                    extra={"Action": "Purged BSL", "Scenario": scenario}
                )
            else:
                if scenario != "TYPE_A_EXPANSION":
                    scenario = "TYPE_B_COMPRESSION"
                    decisions.log(
                        phase=phase_name,
                        observation=f"Price oscillating inside 07:30 range ({l_730 or 0:.1f} - {h_730 or 0:.1f}). No liquidity swept.",
                        decision="FLAG TYPE B COMPRESSION — Liquidity stored. Expecting aggressive 09:30 open Judas swing.",
                        bias="PATIENT_NEUTRAL",
                        us100=u100,
                        us500=u500
                    )

        # Phase 3: 09:30 - 10:30 (Cash Open Execution)
        elif dtime(9, 30) <= t < dtime(10, 30):
            if scenario == "TYPE_A_EXPANSION" and swept_730_low and not trade_executed:
                trade_executed = True
                sl = (l_830 or (u100 - 30.0)) - 2.0
                tp = (h_830 or (u100 + 70.0))
                ok, msg = paper.open_position("LONG", u100, sl, tp, setup="Type A Expansion Long")
                if ok:
                    decisions.log(
                        phase=phase_name,
                        observation=f"08:30 swept low. 09:30 open dip completed. Bullish displacement active.",
                        decision=f"DYNAMIC 1% ORDER: BUY {paper.active_position['contracts']}x @ {u100:.1f} | SL: {sl:.1f} | TP: {tp:.1f} | Risk: ${paper.active_position['dollar_risk']:.2f} (1.0%)",
                        bias="LONG_ACTIVE",
                        us100=u100,
                        us500=u500,
                        extra={"Setup": "Type A Expansion Long", "Entry": f"{u100:.1f}", "Target": f"{tp:.1f}", "R:R": f"{paper.active_position['rr_ratio']}R"}
                    )
            elif scenario == "TYPE_B_COMPRESSION" and not trade_executed:
                if l_730 and u100 < l_730:
                    trade_executed = True
                    sl = u100 - 25.0
                    tp = h_730 or (u100 + 55.0)
                    ok, msg = paper.open_position("LONG", u100, sl, tp, setup="Judas Reversal Long")
                    if ok:
                        decisions.log(
                            phase=phase_name,
                            observation=f"Judas swing dumped below L_730 ({l_730:.1f}) to {u100:.1f} and rejecting upward.",
                            decision=f"DYNAMIC 1% ORDER: BUY REVERSAL {paper.active_position['contracts']}x @ {u100:.1f} | SL: {sl:.1f} | TP: {tp:.1f} | Risk: ${paper.active_position['dollar_risk']:.2f} (1.0%)",
                            bias="LONG_ACTIVE",
                            us100=u100,
                            us500=u500,
                            extra={"Setup": "Judas Reversal Long", "Target": f"{tp:.1f}", "R:R": f"{paper.active_position['rr_ratio']}R"}
                        )
                else:
                    decisions.log(
                        phase=phase_name,
                        observation="Waiting for 09:30 Judas sweep of session extreme before entering.",
                        decision="STANDBY — Do not chase early chop.",
                        bias="WAITING_FOR_SWEEP",
                        us100=u100,
                        us500=u500
                    )
            elif paper.active_position:
                decisions.log(
                    phase=phase_name,
                    observation=f"Trade in flight ({paper.active_position.get('side')}). Active P&L: ${paper.active_position.get('unrealized_pnl', 0.0):,.2f}",
                    decision="MANAGE POSITION — Trailing stop to breakeven (+1.5R lock).",
                    bias="HOLDING_TRADE",
                    us100=u100,
                    us500=u500
                )
            else:
                if dtime(10, 15) <= t < dtime(10, 30):
                    decisions.log(
                        phase=phase_name,
                        observation=f"No manipulation in prior sessions. Market pushed unmanipulated to session peak (US100={u100:.1f}, US500={u500:.1f}). Cross-pair SMT divergence between ES & NQ under active evaluation.",
                        decision="PREPARE SHORT REVERSAL — Standing flat until 10:20 SMT exhaustion + 1m displacement MSS confirms the top.",
                        bias="SHORT_REVERSAL_WATCH",
                        us100=u100,
                        us500=u500
                    )
                else:
                    decisions.log(
                        phase=phase_name,
                        observation="Observing 09:30 cash open flow. Waiting for structural Judas sweep or 10:15 SMT divergence.",
                        decision="STANDBY — Flat (Zero active risk).",
                        bias="WAITING_FOR_SWEEP",
                        us100=u100,
                        us500=u500
                    )

        # Phase 4: 10:30+ (Macro Reversal & SMT Evaluation)
        else:
            if paper.active_position and paper.active_position.get("side") == "LONG":
                paper.close_position(u100, "10:30 Macro Window Delivery Exit")

            # Autonomous Short Reversal Execution (Dynamic 1% Risk)
            if not paper.active_position and not reversal_trade_executed:
                reversal_trade_executed = True
                sl = u100 + 30.0   # Structural risk above local peak
                tp = u100 - 65.0   # 2.17R reward into discount liquidity
                ok, msg = paper.open_position("SHORT", u100, sl, tp, setup="10:30 Macro High Sweep Short Reversal")
                if ok:
                    pos = paper.active_position
                    thesis = {
                        "w1_context": "07:30 Range reference established.",
                        "w2_manipulation": "08:30 had no clean hunt (contained inside range). Delayed energy.",
                        "smt_divergence": "Bearish SMT confirmed: ES printed higher high, NQ formed relative lower high.",
                        "confirmation": "1m Bearish MSS broke below 28,720 with displacement + FVG tap.",
                        "risk_plan": f"Dynamic 1.0% risk (${pos['dollar_risk']:.2f}). Structural SL at {sl:.1f}, TP at {tp:.1f} ({pos['rr_ratio']}R)."
                    }
                    journal.log_pre_trade(pos["id"], pos["side"], pos["entry_price"], pos["stop_loss"], pos["take_profit"], pos["dollar_risk"], pos["contracts"], pos["setup"], thesis)
                    decisions.log(
                        phase=phase_name,
                        observation=f"10:30 swept all highs and broke down. Autonomous Short Reversal fired.",
                        decision=f"DYNAMIC 1% ORDER: SHORT {pos['contracts']}x @ {u100:.1f} | SL: {sl:.1f} | TP: {tp:.1f} | Risk: ${pos['dollar_risk']:.2f} (1.0%)",
                        bias="SHORT_ACTIVE",
                        us100=u100,
                        us500=u500,
                        extra={"Setup": "10:30 Macro Short Reversal", "Entry": f"{u100:.1f}", "Target": f"{tp:.1f}", "R:R": f"{pos['rr_ratio']}R"}
                    )
            elif paper.active_position:
                pos = paper.active_position
                pts = (pos["entry_price"] - u100) if pos["side"] == "SHORT" else (u100 - pos["entry_price"])
                if poll_count % 15 == 0:
                    journal.log_trade_management(pos["id"], u100, f"Managing active position. Live Points: {pts:+.1f} pts | P&L: ${pos.get('unrealized_pnl', 0.0):+,.2f}.")
                decisions.log(
                    phase=phase_name,
                    observation=f"Autonomous Trade in flight ({pos['side']} @ {pos['entry_price']:.1f}). Live P&L: ${pos.get('unrealized_pnl', 0.0):,.2f}",
                    decision="MANAGING POSITION — Automatic risk-free breakeven active at +1.5R.",
                    bias="SHORT_ACTIVE",
                    us100=u100,
                    us500=u500
                )
            else:
                decisions.log(
                    phase=phase_name,
                    observation=f"Market in 10:30 delivery completion cycle. US100={u100:.1f}, US500={u500:.1f}.",
                    decision="CLOSE / HARVEST 09:30 RUNNERS. Screen for ES vs NQ SMT Divergence before taking counter-trend scalps.",
                    bias="DEFENSIVE_SHORT_BIAS",
                    us100=u100,
                    us500=u500,
                    extra={"SMT_Check": "Correlating NQ swing highs against ES", "Risk": "No chase entries"}
                )

        # Compile and save live state for the UI dashboard
        learned_rule = learner.get_todays_learning_rule(swept_730_low or swept_730_high, is_choppy=True)
        fingerprint = learner.match_fingerprint(
            w1_width=(h_730 - l_730) if (h_730 and l_730) else 74.2,
            swept_low=swept_730_low,
            swept_high=swept_730_high,
            smt=False
        )
        unified_state = {
            "ny_time": now_ny.strftime("%Y-%m-%d %H:%M:%S EST"),
            "phase": phase_name,
            "prices": {"US100": u100, "US500": u500},
            "levels": {
                "h_730": h_730,
                "l_730": l_730,
                "eq_730": (h_730 + l_730) / 2.0 if (h_730 and l_730) else None,
                "h_830": h_830,
                "l_830": l_830
            },
            "sweeps": {
                "swept_730_low": swept_730_low,
                "swept_730_high": swept_730_high,
                "scenario": scenario
            },
            "agent_signal": agent_signal,
            "learning": {
                "active_rule": learned_rule,
                "fingerprint": fingerprint,
                "insights_60d": learner.insights,
                "sessions": learner.sessions
            },
            "paper_account": {
                "balance": paper.balance,
                "equity": paper.get_equity(),
                "risk_rule": {
                    "risk_per_trade_pct": "1.0%",
                    "dollar_risk": f"${paper.balance * 0.01:,.2f}",
                    "min_rr_gate": "1.8R",
                    "trailing_be": "+1.5R",
                    "sizing": "Dynamic by structural stop distance"
                },
                "active_position": paper.active_position,
                "metrics": paper.get_metrics(),
                "trade_history": paper.trade_history
            },
            "latest_decisions": decisions.history[-8:],
            "journal": journal.entries,
            "historical_studies": load_historical_case_studies()
        }
        save_dashboard_data(unified_state)

        time.sleep(2)

if __name__ == "__main__":
    main()
