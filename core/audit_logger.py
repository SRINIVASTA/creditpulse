import sqlite3
import os
from datetime import datetime

class ImmutableAuditLogger:
    def __init__(self, db_path="data/audit_trail.db"):
        self.db_path = db_path
        # Create data directory safely if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credit_audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    account_id TEXT,
                    probability_of_default REAL,
                    expected_credit_loss REAL,
                    risk_tag TEXT,
                    human_override_status TEXT DEFAULT 'PENDING_REVIEW'
                )
            """)
            conn.commit()

    def log_decision(self, account_id: str, pd_val: float, ecl_val: float, tag: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credit_audit_logs (timestamp, account_id, probability_of_default, expected_credit_loss, risk_tag)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), str(account_id), float(pd_val), float(ecl_val), tag))
            conn.commit()
