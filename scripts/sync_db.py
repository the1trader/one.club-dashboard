#!/usr/bin/env python3
"""
Synchronizes all trading data (Live Trades, Historical Studies, Journal, Account Metrics)
into both Neon PostgreSQL (if configured) and SQLite (storage.sqlite).
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db import db

def run_sync():
    print("🔄 Starting database synchronization...")
    
    # 1. Sync Live Trades & Metrics
    acct_file = os.path.join(BASE_DIR, "logs", "paper_account.json")
    if os.path.exists(acct_file):
        with open(acct_file, "r") as f:
            acct_data = json.load(f)
        for t in acct_data.get("trade_history", []):
            db.sync_live_trade(t)
        db.sync_account_metrics(acct_data)
        print(f"  ✅ Synced {len(acct_data.get('trade_history', []))} real live tape trades.")

    # 2. Sync Historical Studies
    studies_file = os.path.join(BASE_DIR, "logs", "historical_case_studies.json")
    if os.path.exists(studies_file):
        with open(studies_file, "r") as f:
            studies_data = json.load(f)
        for s in studies_data:
            db.sync_historical_study(s)
        print(f"  ✅ Synced {len(studies_data)} historical retrospective chart studies.")

    # 3. Sync Journal Entries
    journal_file = os.path.join(BASE_DIR, "logs", "trade_journal.json")
    if os.path.exists(journal_file):
        with open(journal_file, "r") as f:
            journal_data = json.load(f)
        for j in journal_data:
            db.sync_journal_entry(j)
        print(f"  ✅ Synced {len(journal_data)} trade journal write-ups.")

    print("🎉 Database synchronization completed successfully!")

if __name__ == "__main__":
    run_sync()
