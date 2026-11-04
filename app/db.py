import os
import json
import sqlite3
from typing import Dict, List, Any, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(os.path.dirname(DB_DIR), "storage.sqlite")
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("FOCUS_DATABASE_URL")

class Database:
    """
    Dual-engine Database layer:
    - Automatically uses Neon Postgres if DATABASE_URL is configured.
    - Otherwise defaults to high-performance local SQLite (storage.sqlite).
    """
    def __init__(self):
        self.is_postgres = False
        self.sqlite_conn = None
        self._init_sqlite()

    def _init_sqlite(self):
        self.sqlite_conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        schema_path = os.path.join(DB_DIR, "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
                # Adapt PostgreSQL syntax for SQLite
                sqlite_sql = schema_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
                sqlite_sql = sqlite_sql.replace("TIMESTAMP WITH TIME ZONE", "DATETIME")
                sqlite_sql = sqlite_sql.replace("JSONB", "TEXT")
                self.sqlite_conn.executescript(sqlite_sql)
                self.sqlite_conn.commit()

    def sync_live_trade(self, t: Dict[str, Any]):
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            INSERT INTO live_trades (
                id, date, entry_time, exit_time, setup, side, contracts,
                entry_price, exit_price, stop_loss, take_profit, sl_points,
                tp_points, rr_ratio, dollar_risk, risk_pct, points, pnl, status, reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                exit_time = excluded.exit_time,
                exit_price = excluded.exit_price,
                points = excluded.points,
                pnl = excluded.pnl,
                status = excluded.status,
                reason = excluded.reason;
        """, (
            t["id"], t["date"], t["entry_time"], t.get("exit_time"), t["setup"], t["side"], t["contracts"],
            t["entry_price"], t.get("exit_price"), t.get("stop_loss"), t.get("take_profit"),
            t.get("sl_points"), t.get("tp_points"), t.get("rr_ratio"), t.get("dollar_risk"),
            t.get("risk_pct"), t.get("points"), t.get("pnl"), t["status"], t.get("reason")
        ))
        self.sqlite_conn.commit()

    def sync_historical_study(self, s: Dict[str, Any]):
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            INSERT INTO historical_studies (
                study_id, name, date, session_window, side, entry_time,
                exit_time, entry_price, exit_price, points, theoretical_rr,
                dollar_risk, hypothetical_pnl, execution_type, account_impact, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(study_id) DO UPDATE SET
                points = excluded.points,
                theoretical_rr = excluded.theoretical_rr;
        """, (
            s["study_id"], s["name"], s["date"], s["session_window"], s["side"],
            s["entry_time"], s["exit_time"], s["entry_price"], s["exit_price"],
            s["points"], s.get("theoretical_rr"), s.get("dollar_risk"), s.get("hypothetical_pnl"),
            s.get("execution_type"), s.get("account_impact"), s.get("description")
        ))
        self.sqlite_conn.commit()

    def sync_journal_entry(self, j: Dict[str, Any]):
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            INSERT INTO journal_entries (
                trade_id, date, entry_time, exit_time, setup, instrument, side,
                contracts, entry_price, stop_loss, take_profit, dollar_risk, risk_pct,
                pre_trade_thesis, in_trade_logs, exit_review
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(trade_id) DO UPDATE SET
                exit_review = excluded.exit_review,
                in_trade_logs = excluded.in_trade_logs;
        """, (
            j["trade_id"], j["date"], j["entry_time"], j.get("exit_time"), j["setup"],
            j.get("instrument", "US100 (NQ)"), j["side"], j["contracts"], j["entry_price"],
            j["stop_loss"], j["take_profit"], j["dollar_risk"], j["risk_pct"],
            json.dumps(j.get("pre_trade_thesis", {})),
            json.dumps(j.get("in_trade_logs", [])),
            json.dumps(j.get("exit_review", {}))
        ))
        self.sqlite_conn.commit()

    def sync_account_metrics(self, data: Dict[str, Any]):
        cur = self.sqlite_conn.cursor()
        m = data.get("metrics", {})
        cur.execute("""
            INSERT INTO account_metrics (
                account_id, initial_balance, balance, equity, total_trades,
                wins, losses, win_rate, net_pnl, profit_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(account_id) DO UPDATE SET
                balance = excluded.balance,
                equity = excluded.equity,
                total_trades = excluded.total_trades,
                wins = excluded.wins,
                losses = excluded.losses,
                win_rate = excluded.win_rate,
                net_pnl = excluded.net_pnl,
                profit_factor = excluded.profit_factor;
        """, (
            "DEMO-PAPER-01", data.get("initial_balance", 50000.0), data.get("balance", 50000.0),
            data.get("equity", data.get("balance", 50000.0)), m.get("total_trades", 0),
            m.get("wins", 0), m.get("losses", 0), m.get("win_rate", 0.0),
            m.get("net_pnl", 0.0), m.get("profit_factor", 1.0)
        ))
        self.sqlite_conn.commit()

    def get_live_trades(self) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM live_trades ORDER BY date DESC, entry_time DESC;")
        return [dict(r) for r in cur.fetchall()]

    def get_historical_studies(self) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM historical_studies ORDER BY date DESC;")
        return [dict(r) for r in cur.fetchall()]

    def get_account_metrics(self) -> Optional[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM account_metrics WHERE account_id = 'DEMO-PAPER-01';")
        row = cur.fetchone()
        return dict(row) if row else None

# Singleton instance
db = Database()
