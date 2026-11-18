import base64
import hashlib
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet


class MemoryVaultService:
    layer_id = "layer-03-memory-vault"
    service_name = "memory-vault"

    def __init__(self, root_dir: Path, secret_seed: bytes):
        self.db_path = Path(root_dir) / "layer-03-memory-vault" / "jroc_os_vault.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        key = base64.urlsafe_b64encode(hashlib.sha256(secret_seed).digest())
        self._fernet = Fernet(key)

    def start(self) -> dict:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS vault_records (
                    record_key TEXT PRIMARY KEY,
                    namespace TEXT NOT NULL,
                    ciphertext BLOB NOT NULL
                );"""
            )
        return {"status": "ready"}

    def put(self, key: str, value: str, namespace: str = "general"):
        if not key or not namespace:
            raise ValueError("Vault key and namespace are required")
        token = self._fernet.encrypt(value.encode("utf-8"))
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                """INSERT INTO vault_records (record_key, namespace, ciphertext)
                   VALUES (?, ?, ?)
                   ON CONFLICT(record_key) DO UPDATE SET
                   ciphertext=excluded.ciphertext, namespace=excluded.namespace;""",
                (key, namespace, token),
            )

    def get(self, key: str):
        with sqlite3.connect(str(self.db_path)) as conn:
            row = conn.execute(
                "SELECT ciphertext FROM vault_records WHERE record_key = ?;", (key,)
            ).fetchone()
        return self._fernet.decrypt(row[0]).decode("utf-8") if row else None

    def health_check(self) -> dict:
        with sqlite3.connect(str(self.db_path)) as conn:
            count = conn.execute("SELECT COUNT(*) FROM vault_records;").fetchone()[0]
        return {"records": count}

    def stop(self) -> dict:
        return {"status": "stopped"}
