from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("AUDITOR_DB", "data/auditor.db")


def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset TEXT NOT NULL,
            ts TEXT,
            bet_id TEXT,
            server_seed TEXT,
            server_seed_hash TEXT,
            client_seed TEXT NOT NULL,
            nonce INTEGER NOT NULL,
            round_no INTEGER NOT NULL,
            reported_result INTEGER NOT NULL,
            algorithm TEXT NOT NULL,
            expected_result INTEGER,
            result_match INTEGER,
            seed_hash_match INTEGER,
            amount REAL,
            payout_multiplier REAL,
            row_fingerprint TEXT
        )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_bets_dataset ON bets(dataset)")
        try:
            con.execute("ALTER TABLE bets ADD COLUMN row_fingerprint TEXT")
        except sqlite3.OperationalError:
            pass
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_bets_dataset_rowfp "
                    "ON bets(dataset, row_fingerprint) WHERE row_fingerprint IS NOT NULL")
