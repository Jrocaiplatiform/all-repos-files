import sqlite3, threading
from contextlib import contextmanager
from pathlib import Path

class SQLiteManager:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @contextmanager
    def connection(self):
        with self._lock:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def execute(self, sql: str, params=()):
        with self.connection() as conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid or cur.rowcount

    def fetch_one(self, sql: str, params=()):
        with self.connection() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None