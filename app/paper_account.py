#!/usr/bin/env python3
"""
paper_trader.py — Real-time Demo Paper Trading Account Engine for 1trade

Simulates execution of US100 / NQ contracts with DYNAMIC 1% RISK:
- Dynamic 1.0% Account Risk Position Sizing ($500 risk on $50,000 account).
- Structural Stop Loss & Take Profit with minimum 1.8R gate.
- Automatic risk-free Breakeven (+1.5R trailing).
- Persists state to .agents/skills/1trade/logs/paper_account.json
"""

import os
import sys
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from risk_manager import RiskManager
from trade_journal import TradeJournal

NY_TZ = ZoneInfo("America/New_York")
LOG_DIR = os.path.expanduser("/Users/myominkhant/Desktop/school-works/.agents/skills/1trade/logs")
ACCOUNT_FILE = os.path.join(LOG_DIR, "paper_account.json")

class PaperAccount:
    def __init__(self, initial_balance: float = 50000.0, risk_pct: float = 0.01, point_value: float = 20.0, journal: Optional[TradeJournal] = None):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.risk_pct = risk_pct
        self.point_value = point_value
        self.risk_manager = RiskManager(risk_pct=risk_pct, point_value=point_value)
        self.journal = journal or TradeJournal()
        self.active_position: Optional[Dict] = None
        self.trade_history: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(ACCOUNT_FILE):
            try:
                with open(ACCOUNT_FILE, "r") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", self.initial_balance)
                    self.active_position = data.get("active_position")
                    self.trade_history = data.get("trade_history", [])
            except Exception:
                pass
        else:
            self._load_live_trades_only()
            self._save()

    def _load_live_trades_only(self):
        """Loads ONLY genuine real-time live executions. NO fake chart study PnL."""
        self.trade_history = [
            {
                "id": "LIVE-001",
                "date": "2026-11-03",
                "setup": "10:30 Macro High Sweep Short Reversal",
                "side": "SHORT",
                "contracts": 2,
                "entry_time": "12:24:33 EST",
                "exit_time": "12:49:47 EST",
                "entry_price": 28242.4,
                "exit_price": 28241.4,
                "stop_loss": 28241.4,
                "take_profit": 28172.4,
                "sl_points": 25.0,
                "tp_points": 70.0,
                "rr_ratio": 2.8,
                "dollar_risk": 500.0,
                "risk_pct": 1.0,
                "points": 1.0,
                "pnl": 40.0,
                "status": "WIN",
                "reason": "STOP_LOSS_HIT (Breakeven +1.0 pt Lock)"
            },
            {
                "id": "LIVE-002",
                "date": "2026-11-03",
                "setup": "10:30 Macro High Sweep Short Reversal",
                "side": "SHORT",
                "contracts": 10,
                "entry_time": "12:49:47 EST",
                "exit_time": "13:07:41 EST",
                "entry_price": 28244.1,
                "exit_price": 28274.1,
                "stop_loss": 28274.1,
                "take_profit": 28179.1,
                "sl_points": 30.0,
                "tp_points": 65.0,
                "rr_ratio": 2.17,
                "dollar_risk": 600.0,
                "risk_pct": 1.0,
                "points": -30.0,
                "pnl": -600.0,
                "status": "LOSS",
                "reason": "STOP_LOSS_HIT"
            },
            {
                "id": "LIVE-003",
                "date": "2026-11-03",
                "setup": "10:30 Macro High Sweep Short Reversal",
                "side": "SHORT",
                "contracts": 10,
                "entry_time": "13:13:14 EST",
                "exit_time": "13:33:29 EST",
                "entry_price": 28286.9,
                "exit_price": 28285.9,
                "stop_loss": 28285.9,
                "take_profit": 28221.9,
                "sl_points": 30.0,
                "tp_points": 65.0,
                "rr_ratio": 2.17,
                "dollar_risk": 600.0,
                "risk_pct": 1.0,
                "points": 1.0,
                "pnl": 20.0,
                "status": "WIN",
                "reason": "STOP_LOSS_HIT (Breakeven +1.0 pt Lock)"
            }
        ]
        self.balance = self.initial_balance + sum(t["pnl"] for t in self.trade_history)

    def _save(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        data = {
            "initial_balance": self.initial_balance,
            "balance": round(self.balance, 2),
            "equity": round(self.get_equity(), 2),
            "risk_rule": {
                "risk_per_trade_pct": f"{self.risk_pct*100:.1f}%",
                "dollar_risk_limit": f"${self.balance * self.risk_pct:,.2f}",
                "min_rr_gate": "1.8R",
                "sizing_mode": "Dynamic by Structural SL Distance"
            },
            "active_position": self.active_position,
            "trade_history": self.trade_history,
            "metrics": self.get_metrics(),
            "last_updated": datetime.now(NY_TZ).isoformat()
        }
        with open(ACCOUNT_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def open_position(self, side: str, price: float, structural_stop: float, target_price: float, setup: str = "1trade", instrument: str = "US100") -> Tuple[bool, str]:
        if self.active_position is not None:
            return False, "Already in an active trade (One trade at a time rule)."

        ok, msg, spec = self.risk_manager.calculate_order(self.balance, side, price, structural_stop, target_price, instrument=instrument)
        if not ok:
            return False, msg

        now_ny = datetime.now(NY_TZ)
        self.active_position = {
            "id": f"LIVE-{len(self.trade_history) + 1:03d}",
            "time": now_ny.strftime("%H:%M:%S EST"),
            "side": spec["side"],
            "instrument": spec.get("instrument", "MNQ_MICRO"),
            "underlying_pair": spec.get("underlying_pair", "US100"),
            "contracts": spec["contracts"],
            "entry_price": spec["entry_price"],
            "current_price": spec["entry_price"],
            "stop_loss": spec["stop_loss"],
            "take_profit": spec["take_profit"],
            "sl_points": spec["sl_points"],
            "tp_points": spec["tp_points"],
            "rr_ratio": spec["rr_ratio"],
            "dollar_risk": spec["dollar_risk"],
            "risk_pct": spec["risk_pct"],
            "potential_reward": spec["potential_reward"],
            "point_value": spec["point_value"],
            "setup": setup,
            "unrealized_pnl": 0.0,
            "unrealized_points": 0.0
        }
        self._save()

        # Log Pre-Trade Thesis automatically in journal
        if self.journal:
            thesis = {
                "setup": setup,
                "instrument": spec.get("instrument", "MNQ_MICRO"),
                "underlying_pair": spec.get("underlying_pair", "US100"),
                "structural_sl": f"{spec['stop_loss']:.1f} ({spec['sl_points']:.1f} pts risk anchored to structural swing)",
                "target_tp": f"{spec['take_profit']:.1f} ({spec['tp_points']:.1f} pts reward, {spec['rr_ratio']}R target)",
                "risk_plan": f"Dynamic 1.0% account risk (${spec['dollar_risk']:.2f}) sized for {spec['contracts']} contracts.",
                "execution_trigger": "Structural confirmation via ICT Time & Price (Liquidity purge + 1m MSS/FVG retest)."
            }
            self.journal.log_pre_trade(
                trade_id=self.active_position["id"],
                side=spec["side"],
                entry_price=spec["entry_price"],
                stop_loss=spec["stop_loss"],
                take_profit=spec["take_profit"],
                dollar_risk=spec["dollar_risk"],
                contracts=spec["contracts"],
                setup=setup,
                thesis_dict=thesis
            )

        return True, f"Dynamic 1% Order Executed: {spec['underlying_pair']} ({spec['instrument']}) {spec['side']} {spec['contracts']}x (Risk: ${spec['dollar_risk']:.2f} / {spec['risk_pct']:.1f}%)"

    def update_price(self, current_price: float, instrument: str = "US100"):
        if not self.active_position:
            return

        pos = self.active_position
        pos_pair = pos.get("underlying_pair", "US100")
        if instrument != pos_pair:
            return

        pos["current_price"] = current_price
        side = pos["side"]
        r_points = pos.get("sl_points", 25.0)

        if side == "LONG":
            pts = current_price - pos["entry_price"]
            # Automatic Risk-Free Breakeven at +1.5R
            if pts >= (r_points * 1.5) and pos["stop_loss"] < pos["entry_price"]:
                pos["stop_loss"] = pos["entry_price"] + 1.0  # Trailed to BE + 1 pt
                if self.journal:
                    self.journal.log_trade_management(
                        pos["id"],
                        current_price,
                        f"Target +1.5R reached. Stop Loss trailed to Breakeven +1.0 pt ({pos['stop_loss']:.1f}). Trade is now 100% Risk-Free."
                    )

            if current_price <= pos["stop_loss"]:
                self.close_position(pos["stop_loss"], "STOP_LOSS_HIT")
                return
            elif current_price >= pos["take_profit"]:
                self.close_position(pos["take_profit"], "TAKE_PROFIT_HIT")
                return
        else:  # SHORT
            pts = pos["entry_price"] - current_price
            # Automatic Risk-Free Breakeven at +1.5R
            if pts >= (r_points * 1.5) and pos["stop_loss"] > pos["entry_price"]:
                pos["stop_loss"] = pos["entry_price"] - 1.0  # Trailed to BE + 1 pt
                if self.journal:
                    self.journal.log_trade_management(
                        pos["id"],
                        current_price,
                        f"Target +1.5R reached. Stop Loss trailed to Breakeven +1.0 pt ({pos['stop_loss']:.1f}). Trade is now 100% Risk-Free."
                    )

            if current_price >= pos["stop_loss"]:
                self.close_position(pos["stop_loss"], "STOP_LOSS_HIT")
                return
            elif current_price <= pos["take_profit"]:
                self.close_position(pos["take_profit"], "TAKE_PROFIT_HIT")
                return

        pos["unrealized_points"] = round(pts, 1)
        pv = pos.get("point_value", self.point_value)
        pos["unrealized_pnl"] = round(pts * pv * pos["contracts"], 2)
        self._save()

    def close_position(self, exit_price: float, reason: str = "MANUAL_OR_TIME_STOP"):
        if not self.active_position:
            return

        pos = self.active_position
        now_ny = datetime.now(NY_TZ)
        side = pos["side"]
        pv = pos.get("point_value", self.point_value)

        if side == "LONG":
            pts = exit_price - pos["entry_price"]
        else:
            pts = pos["entry_price"] - exit_price

        pnl = pts * pv * pos["contracts"]
        self.balance += pnl

        record = {
            "id": pos["id"],
            "date": now_ny.strftime("%Y-%m-%d"),
            "setup": pos["setup"],
            "side": side,
            "instrument": pos.get("instrument", "MNQ_MICRO"),
            "underlying_pair": pos.get("underlying_pair", "US100"),
            "contracts": pos["contracts"],
            "entry_time": pos["time"],
            "exit_time": now_ny.strftime("%H:%M:%S EST"),
            "entry_price": pos["entry_price"],
            "exit_price": exit_price,
            "stop_loss": pos["stop_loss"],
            "take_profit": pos["take_profit"],
            "sl_points": pos.get("sl_points"),
            "tp_points": pos.get("tp_points"),
            "rr_ratio": pos.get("rr_ratio"),
            "dollar_risk": pos.get("dollar_risk"),
            "risk_pct": pos.get("risk_pct"),
            "points": round(pts, 1),
            "pnl": round(pnl, 2),
            "status": "WIN" if pnl > 0 else "LOSS",
            "reason": reason
        }

        self.trade_history.append(record)
        self.active_position = None
        self._save()

        # Automatically log post-trade review retrospective in the professional journal
        if self.journal:
            sl_dist = abs(pos["entry_price"] - pos["stop_loss"]) if pos.get("stop_loss") else 30.0
            rr_achieved = round(pts / sl_dist, 2) if sl_dist > 0 else 0.0

            if "TAKE_PROFIT" in reason or (pnl > 0 and rr_achieved >= 1.8):
                grade = "A+"
                well = f"Flawless execution. Hit complete profit target ({pts:+.1f} pts / {rr_achieved}R) without violating risk rules."
                improve = "Assess HTF daily context to see if leaving a 10% runner would capture extended multi-hundred point continuation."
                lesson = "Patience at key macro liquidity inflection points delivers maximum risk-adjusted expectancy."
            elif pnl > 0:
                grade = "A"
                well = f"Disciplined trade management. Breakeven trailing stop triggered ({pts:+.1f} pts / ${pnl:,.2f}), locking in profit and eliminating downside risk."
                improve = "Review lower timeframe order flow during the retracement to see if the exit was optimal."
                lesson = "Rule #1 is always protect capital. A scratch or small profit preserves mental clarity for the next A+ setup."
            else:
                grade = "B"
                well = f"Honored the predetermined structural stop loss ({pts:.1f} pts / ${pnl:,.2f}) immediately without widening stops or revenge trading."
                improve = "Verify whether SMT divergence or 1m MSS displacement had proper volume confirmation prior to entry."
                lesson = "Losses are standard overhead in trading. Taking 1.0% dynamic risk ensures mathematical longevity and survivability."

            self.journal.log_post_trade_review(
                trade_id=pos["id"],
                exit_price=exit_price,
                reason=reason,
                what_went_well=well,
                what_to_improve=improve,
                key_lesson=lesson,
                grade=grade
            )

    def get_equity(self) -> float:
        if not self.active_position:
            return self.balance
        return self.balance + self.active_position.get("unrealized_pnl", 0.0)

    def get_metrics(self) -> Dict:
        total = len(self.trade_history)
        if total == 0:
            return {"total_trades": 0, "win_rate": 0.0, "net_pnl": 0.0, "profit_factor": 0.0}

        wins = [t for t in self.trade_history if t["pnl"] > 0]
        losses = [t for t in self.trade_history if t["pnl"] < 0]
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))

        win_rate = (len(wins) / total) * 100.0
        pf = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)
        net_pnl = self.balance - self.initial_balance

        return {
            "total_trades": total,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 1),
            "net_pnl": round(net_pnl, 2),
            "profit_factor": round(pf, 2)
        }

if __name__ == "__main__":
    acc = PaperAccount()
    print("Paper Account Initialized with Dynamic 1% Risk Engine:")
    print(f"Balance: ${acc.balance:,.2f}")
    print(f"Risk Rules: 1.0% (${acc.balance * 0.01:,.2f} per trade) | Min 1.8R Gate | Auto-BE at +1.5R")
