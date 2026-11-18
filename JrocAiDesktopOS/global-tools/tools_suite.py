import re
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path


class GlobalToolsSuite:
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir).resolve()
        self.db_path = self.root_dir / "data" / "global_tools.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.root_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, status TEXT DEFAULT 'queued');"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS apps (app_id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL);"
            )

    def search_files(self, query: str) -> list:
        q = query.lower().strip()
        if not q:
            return []
        excluded = {".git", "__pycache__", "backups"}
        return [
            str(path.relative_to(self.root_dir))
            for path in self.root_dir.rglob("*")
            if path.is_file()
            and not excluded.intersection(path.parts)
            and q in path.name.lower()
        ]

    def add_task(self, title: str) -> int:
        if not title.strip():
            raise ValueError("Task title is required")
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("INSERT INTO tasks (title) VALUES (?);", (title.strip(),))
            return int(cursor.lastrowid)

    def list_tasks(self) -> list:
        with sqlite3.connect(str(self.db_path)) as conn:
            return [
                {"id": row[0], "title": row[1], "status": row[2]}
                for row in conn.execute("SELECT id, title, status FROM tasks;").fetchall()
            ]

    def install_app(self, app_id: str, name: str, version: str) -> dict:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO apps (app_id, name, version) VALUES (?, ?, ?);",
                (app_id, name, version),
            )
        return {"app_id": app_id, "status": "registered"}

    def verify_databases(self) -> list:
        results = []
        for database in self.root_dir.rglob("*.db"):
            if {".git", "__pycache__", "backups"}.intersection(database.parts):
                continue
            with sqlite3.connect(str(database)) as conn:
                result = conn.execute("PRAGMA integrity_check;").fetchone()
            results.append({"db": str(database.relative_to(self.root_dir)), "ok": result[0] == "ok"})
        return results

    def create_snapshot(self, label: str = "auto") -> Path:
        safe_label = re.sub(r"[^A-Za-z0-9_-]", "_", label).strip("_") or "auto"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = self.backup_dir / f"jroc_{safe_label}_{timestamp}.zip"
        excluded = {".git", "__pycache__", "backups"}
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for pattern in ("*.py", "*.json", "*.yaml", "*.db"):
                for item in self.root_dir.rglob(pattern):
                    if not excluded.intersection(item.parts):
                        archive.write(item, arcname=str(item.relative_to(self.root_dir)))
        return archive_path
