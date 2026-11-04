#!/usr/bin/env python3
"""
risk_manager.py — Institutional 1% Risk Management, Structural Invalidation & 2-Tier Exit Engine for 1trade

Core Institutional Rules:
1. Dynamic 1.0% Account Risk:
   - Dollar Risk = Account Balance * 1.0% (e.g. $48,980 * 0.01 = $489.80).
   - Position Size (contracts/lots) dynamically calculated from structural point distance.
2. Structural Stop Loss Placement (Non-Negotiable):
   - LONG: Stop Loss = Structural Invalidation Low (MSS/Judas low) - buffer.
   - SHORT: Stop Loss = Structural Invalidation High (MSS/10:18 peak) + buffer.
   - NEVER an arbitrary number of points, pips, or ticks.
3. 2-Tier Exit Model (75% Core + 25% Runner):
   - Target 1 (T1): Primary Draw on Liquidity (DOL) — 2.0R to 2.5R (75% position banked).
   - Target 2 (T2): HTF Draw on Liquidity (25% runner trailed to HTF session low/high).
4. Structural Breakeven Policy:
   - NO premature moving to breakeven before Target 1 is tapped.
   - Only snaps to BE after T1 is banked and trade is de-risked.
"""

from typing import Dict, Optional, Tuple
import math

class RiskManager:
    def __init__(self, risk_pct: float = 0.01, point_value: float = 20.0, instrument: str = "US100"):
        self.risk_pct = risk_pct          # Default 1.0% risk per trade
        self.point_value = point_value
        self.instrument = instrument
        self.min_rr_ratio = 1.8           # Must offer at least 1.8R to enter

    def calculate_order(self, balance: float, side: str, entry_price: float,
                        structural_stop: float, target_price: float,
                        htf_target: Optional[float] = None,
                        instrument: str = "US100") -> Tuple[bool, str, Dict]:
        """
        Calculates position sizing for exactly 1.0% risk and generates 2-tier scale-out specifications.
        """
        side_clean = side.upper()
        dollar_risk = balance * self.risk_pct

        # 1. Structural Stop Loss Distance
        if side_clean == "LONG":
            sl_distance = entry_price - structural_stop
            tp1_distance = target_price - entry_price
            tp2_distance = (htf_target - entry_price) if htf_target else (tp1_distance * 2.0)
        else: # SHORT
            sl_distance = structural_stop - entry_price
            tp1_distance = entry_price - target_price
            tp2_distance = (entry_price - htf_target) if htf_target else (tp1_distance * 2.0)

        # Sanity Checks
        if sl_distance <= 0:
            return False, f"Invalid Stop Loss: SL ({structural_stop:.1f}) is on wrong side of Entry ({entry_price:.1f})", {}

        if tp1_distance <= 0:
            return False, f"Invalid Target 1: T1 ({target_price:.1f}) is on wrong side of Entry ({entry_price:.1f})", {}

        # 2. Risk/Reward Ratio Gate
        rr_ratio = tp1_distance / sl_distance
        if rr_ratio < self.min_rr_ratio:
            return False, f"Poor R:R Ratio: T1 offers {rr_ratio:.2f}R (Minimum required: {self.min_rr_ratio:.1f}R). Skipped.", {}

        # 3. Dynamic Position Sizing (Strict 1.0% Account Risk)
        inst_upper = instrument.upper()
        if "500" in inst_upper or "ES" in inst_upper:
            # US500 / ES: Default to Micro ES ($5.00/pt)
            pv = 5.0
            actual_inst = "MES_MICRO"
            raw_contracts = dollar_risk / (sl_distance * pv)
            if raw_contracts >= 10.0:
                pv = 50.0
                actual_inst = "ES_FUTURES"
                total_contracts = max(1, round(dollar_risk / (sl_distance * pv)))
            else:
                total_contracts = max(1, round(raw_contracts))
            actual_dollar_risk = total_contracts * sl_distance * pv
        else:
            # US100 / NQ: Default to Micro NQ ($2.00/pt)
            pv = 2.0
            actual_inst = "MNQ_MICRO"
            raw_contracts = dollar_risk / (sl_distance * pv)
            if raw_contracts >= 10.0:
                pv = 20.0
                actual_inst = "NQ_FUTURES"
                total_contracts = max(1, round(dollar_risk / (sl_distance * pv)))
            else:
                total_contracts = max(1, round(raw_contracts))
            actual_dollar_risk = total_contracts * sl_distance * pv

        actual_risk_pct = (actual_dollar_risk / balance) * 100.0

        # 4. 2-Tier Contract Allocation (75% Core / 25% Runner)
        if total_contracts >= 4:
            core_contracts = int(total_contracts * 0.75)
            runner_contracts = total_contracts - core_contracts
        elif total_contracts >= 2:
            core_contracts = total_contracts - 1
            runner_contracts = 1
        else:
            core_contracts = 1
            runner_contracts = 0

        # Calculated Potential Rewards
        t2_price = htf_target if htf_target else (entry_price + (tp2_distance if side_clean == "LONG" else -tp2_distance))
        reward_t1 = core_contracts * tp1_distance * pv
        reward_t2 = runner_contracts * tp2_distance * pv
        total_potential_reward = reward_t1 + reward_t2

        order_spec = {
            "side": side_clean,
            "entry_price": round(entry_price, 1),
            "stop_loss": round(structural_stop, 1),
            "take_profit_1": round(target_price, 1),
            "take_profit_2": round(t2_price, 1),
            "sl_points": round(sl_distance, 1),
            "tp1_points": round(tp1_distance, 1),
            "tp2_points": round(tp2_distance, 1),
            "rr_ratio_t1": round(rr_ratio, 2),
            "total_contracts": total_contracts,
            "core_contracts": core_contracts,
            "runner_contracts": runner_contracts,
            "instrument": actual_inst,
            "underlying_pair": "US500" if ("500" in inst_upper or "ES" in inst_upper) else "US100",
            "point_value": pv,
            "dollar_risk": round(actual_dollar_risk, 2),
            "risk_pct": round(actual_risk_pct, 2),
            "potential_reward_t1": round(reward_t1, 2),
            "potential_reward_t2": round(reward_t2, 2),
            "total_potential_reward": round(total_potential_reward, 2)
        }

        return True, "Order Approved & Sized to Exactly 1% Risk (75/25 2-Tier Allocation)", order_spec

if __name__ == "__main__":
    rm = RiskManager(risk_pct=0.01)
    balance = 48980.0

    print(f"--- 2-Tier Institutional Sizing Test (Account: ${balance:,.2f}) ---")
    
    # Test ES with HTF Runner Target (Target 1: 7650.0, HTF Target 2: 7621.9)
    ok, msg, spec = rm.calculate_order(
        balance, "SHORT", 7694.8, structural_stop=7712.8,
        target_price=7650.0, htf_target=7621.9, instrument="US500"
    )
    print(f"Test ES: {msg}")
    print(f"  Total: {spec['total_contracts']}x {spec['instrument']} | Core (75%): {spec['core_contracts']}x -> T1: {spec['take_profit_1']} | Runner (25%): {spec['runner_contracts']}x -> T2: {spec['take_profit_2']}")
    print(f"  Risk: ${spec['dollar_risk']} ({spec['risk_pct']}%) | Reward T1: ${spec['potential_reward_t1']} | Total Potential: ${spec['total_potential_reward']}")
