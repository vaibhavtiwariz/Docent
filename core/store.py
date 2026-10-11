# core/store.py
"""SQLite persistence for human-in-the-loop corrections.

Every time a curator reviews and corrects the AI-extracted metadata in the
Streamlit UI, the before/after pair is stored here. This closes the
human-in-the-loop loop: corrections accumulate into a dataset that can be
used to evaluate and improve the extractor.
"""

import json
import os
import sqlite3
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corrections.db")


def init_db() -> None:
    con = sqlite3.connect(DB_PATH)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            extracted_title TEXT,
            extracted_authors TEXT,
            corrected_title TEXT,
            corrected_authors TEXT,
            created_at TEXT
        )
        """
    )
    con.commit()
    con.close()


def save_correction(filename: str, extracted_title: str, extracted_authors: list,
                    corrected_title: str, corrected_authors: list) -> int:
    """Store one reviewed correction. Returns the new row id."""
    init_db()
    con = sqlite3.connect(DB_PATH)
    cur = con.execute(
        "INSERT INTO corrections "
        "(filename, extracted_title, extracted_authors, corrected_title, corrected_authors, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            filename,
            extracted_title,
            json.dumps(extracted_authors),
            corrected_title,
            json.dumps(corrected_authors),
            datetime.datetime.utcnow().isoformat() + "Z",
        ),
    )
    con.commit()
    row_id = cur.lastrowid
    con.close()
    return row_id


def get_corrections() -> list:
    """Return all stored corrections as dicts (newest first)."""
    init_db()
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM corrections ORDER BY id DESC").fetchall()
    con.close()
    return [dict(r) for r in rows]
