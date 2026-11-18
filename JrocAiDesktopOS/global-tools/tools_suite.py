import json, sqlite3, zipfile
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
            conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, status TEXT DEFAULT 'queued');")
            conn.execute("CREATE TABLE IF NOT EXISTS apps (app_id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL);")

    def search_files(self, query: str) -> list:
        q = query.lower().strip()
        return [str(p.relative_to(self.root_dir)) for p in self.root_dir.rglob("*") if p.is_file() and q in p.name.lower()]

    def add_task(self, title: str) -> int:
        with sqlite3.connect(str(self.db_path)) as conn:
            cur = conn.execute("INSERT INTO tasks (title) VALUES (?);", (title,))
            return int(cur.lastrowid)

    def list_tasks(self) -> list:
        with sqlite3.connect(str(self.db_path)) as conn:
            return [{"id": r[0], "title": r[1], "status": r[2]} for r in conn.execute("SELECT id, title, status FROM tasks;").fetchall()]

    def install_app(self, app_id: str, name: str, version: str) -> dict:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("INSERT OR REPLACE INTO apps (app_id, name, version) VALUES (?, ?, ?);", (app_id, name, version))
        return {"app_id": app_id, "status": "installed"}

    def verify_databases(self) -> list:
        out = []
        for db in self.root_dir.rglob("*.db"):
            with sqlite3.connect(str(db)) as conn:
                row = conn.execute("PRAGMA integrity_check;").fetchone()
                out.append({"db": db.name, "ok": next(iter(row)) == "ok"})
        return out

    def create_snapshot(self, label: str = "auto") -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"Z)
        zip_path = self.backup_dir / f"jroc_{label}_{stamp}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for ext in ("*.py", "*.json", "*.yaml", "*.db"):
                for item in self.root_dir.rglob(ext):
                    if "backups" not in item.parts:
                        zf.write(item, arcname=str(item.relative_to(self.root_dir)))
       return zip_path
