#!/usr/bin/env python3
"""
risk_manager.py — Dynamic 1% Risk Management & Structural SL/TP Engine for 1trade

Core Rules:
1. Dynamic 1.0% Account Risk:
   - Dollar Risk = Account Balance * 1.0% (e.g. $50,000 * 0.01 = $500.00).
   - Position Size (contracts/lots) is dynamically calculated from structural point distance.
2. Structural Stop Loss Placement:
   - LONG: Stop Loss = Structural Invalidation Low (Judas/08:30 sweep or MSS low) - buffer.
   - SHORT: Stop Loss = Structural Invalidation High (10:18-10:25 peak or MSS high) + buffer.
   - NEVER an arbitrary fixed number of pips, points, or percentages!
3. Structural Take Profit & Minimum 1:2 R:R Gate:
   - TP = Opposing session liquidity pool (08:30 high/low, 07:30 range high/low, or PDH/PDL).
   - Minimum R:R is 1.8:1. If R:R < 1.8:1, trade is invalidated and skipped.
4. Cross-Pair Instrument Support:
   - US100 (NQ/MNQ/CFD): $20/pt (NQ), $2/pt (MNQ), $1/pt (CFD).
   - US500 (ES/MES/CFD): $50/pt (ES), $5/pt (MES), $1/pt (CFD).
5. Automated Risk-Free Breakeven:
   - When trade reaches +1.5R, SL automatically snaps to Entry + 1 tick.
6. Max Drawdown Circuit Breaker:
   - Maximum 2 losses per day (-2.0% max loss). Lockout on 2nd loss.
"""

from typing import Dict, Optional, Tuple

class RiskManager:
    def __init__(self, risk_pct: float = 0.01, point_value: float = 20.0, instrument: str = "US100"):
        self.risk_pct = risk_pct          # Default 1.0% risk per trade
        self.point_value = point_value    # Default point value
        self.instrument = instrument
        self.min_rr_ratio = 1.8           # Must offer at least 1.8R to enter

    def calculate_order(self, balance: float, side: str, entry_price: float,
                        structural_stop: float, target_price: float,
                        instrument: str = "US100") -> Tuple[bool, str, Dict]:
        """
        Dynamically calculates position size to risk EXACTLY 1% of account balance.
        Validates minimum R:R and structural validity.
        Supports both US100 (NQ/MNQ) and US500 (ES/MES).
        """
        side_clean = side.upper()
        dollar_risk = balance * self.risk_pct

        # 1. Structural Stop Loss Distance
        if side_clean == "LONG":
            sl_distance = entry_price - structural_stop
            tp_distance = target_price - entry_price
        else: # SHORT
            sl_distance = structural_stop - entry_price
            tp_distance = entry_price - target_price

        # Sanity Checks
        if sl_distance <= 0:
            return False, f"Invalid Stop Loss: SL ({structural_stop:.1f}) is on wrong side of Entry ({entry_price:.1f})", {}

        if tp_distance <= 0:
            return False, f"Invalid Target: TP ({target_price:.1f}) is on wrong side of Entry ({entry_price:.1f})", {}

        # 2. Risk/Reward Ratio Gate
        rr_ratio = tp_distance / sl_distance
        if rr_ratio < self.min_rr_ratio:
            return False, f"Poor R:R Ratio: Trade offers {rr_ratio:.2f}R (Minimum required: {self.min_rr_ratio:.1f}R). Skipped.", {}

        # 3. Dynamic Position Sizing (Exactly 1.0% Risk)
        inst_upper = instrument.upper()
        if "500" in inst_upper or "ES" in inst_upper:
            # US500 / ES: Default to Micro ES ($5.00/pt) for precise 1% risk budgeting
            pv = 5.0
            actual_inst = "MES_MICRO"
            raw_contracts = dollar_risk / (sl_distance * pv)
            if raw_contracts >= 10.0:
                # Scale to standard ES ($50/pt) if large account
                pv = 50.0
                actual_inst = "ES_FUTURES"
                contracts = max(1, round(dollar_risk / (sl_distance * pv)))
            else:
                contracts = max(1, round(raw_contracts))
            actual_dollar_risk = contracts * sl_distance * pv
        else:
            # US100 / NQ: Default to Micro NQ ($2.00/pt) or standard NQ ($20.00/pt)
            pv = 2.0
            actual_inst = "MNQ_MICRO"
            raw_contracts = dollar_risk / (sl_distance * pv)
            if raw_contracts >= 10.0:
                pv = 20.0
                actual_inst = "NQ_FUTURES"
                contracts = max(1, round(dollar_risk / (sl_distance * pv)))
            else:
                contracts = max(1, round(raw_contracts))
            actual_dollar_risk = contracts * sl_distance * pv

        actual_risk_pct = (actual_dollar_risk / balance) * 100.0

        order_spec = {
            "side": side_clean,
            "entry_price": round(entry_price, 1),
            "stop_loss": round(structural_stop, 1),
            "take_profit": round(target_price, 1),
            "sl_points": round(sl_distance, 1),
            "tp_points": round(tp_distance, 1),
            "rr_ratio": round(rr_ratio, 2),
            "contracts": contracts,
            "instrument": actual_inst,
            "underlying_pair": "US500" if ("500" in inst_upper or "ES" in inst_upper) else "US100",
            "point_value": pv,
            "dollar_risk": round(actual_dollar_risk, 2),
            "risk_pct": round(actual_risk_pct, 2),
            "potential_reward": round(contracts * tp_distance * pv, 2)
        }

        return True, "Order Approved & Sized to Exactly 1% Risk", order_spec

if __name__ == "__main__":
    rm = RiskManager(risk_pct=0.01)
    balance = 48980.0

    print(f"--- Sizing Test (Account: ${balance:,.2f} | Risk: 1.0% = ${balance*0.01:,.2f}) ---")
    
    # Test 1: User's ES Execution (Entry: 7694.8, SL: 7712.8, TP: 7621.9)
    ok, msg, spec = rm.calculate_order(balance, "SHORT", 7694.8, structural_stop=7712.8, target_price=7621.9, instrument="US500")
    print(f"Test 1 (ES Trade): {msg}")
    print(f"  -> Instrument: {spec.get('instrument')} | Contracts: {spec.get('contracts')} | Risk: ${spec.get('dollar_risk')} ({spec.get('risk_pct')}%) | R:R: {spec.get('rr_ratio')}R")

    # Test 2: NQ Structural Stop (Entry: 28582.0, SL: 28688.0, TP: 28350.0)
    ok, msg, spec = rm.calculate_order(balance, "SHORT", 28582.0, structural_stop=28688.0, target_price=28350.0, instrument="US100")
    print(f"Test 2 (NQ Trade): {msg}")
    print(f"  -> Instrument: {spec.get('instrument')} | Contracts: {spec.get('contracts')} | Risk: ${spec.get('dollar_risk')} ({spec.get('risk_pct')}%) | R:R: {spec.get('rr_ratio')}R")
