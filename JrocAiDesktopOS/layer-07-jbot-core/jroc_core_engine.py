import json
import sqlite3
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
LOCAL_MODEL = "llama3.2"


class JrocDesktopOSEngine:
    """Legacy HUD adapter. All inference is sent only to the local Ollama endpoint."""

    def __init__(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(VAULT_DB))
        self._init_layers()

    def _init_layers(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS memory_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, division TEXT, key TEXT UNIQUE, value TEXT, updated_at TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS guardrail_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, swarm_name TEXT, action_type TEXT, payload TEXT, status TEXT DEFAULT 'PENDING_APPROVAL', created_at TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS model_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, model_used TEXT, division TEXT, latency_ms INTEGER, success INTEGER, timestamp TEXT)"
        )
        self.conn.commit()

    def save_memory(self, division, key, value):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO memory_vault (division, key, value, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (division, key, value, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def dispatch_to_swarm(self, division, user_command):
        profiles = {
            "DEV_OPS": "You are the J-ROC AI Factory Dev Swarm. Propose safe, reviewable software work.",
            "REPAIR_PRO": "You are the Universal Repair PRO Swarm. Diagnose device issues safely.",
            "COMMERCE": "You are the J-ROC AI Commerce Swarm. Analyze products and draft listings.",
            "STUDIO": "You are the J-ROC Entertainment Studio Swarm. Develop original creative concepts.",
        }
        system_prompt = profiles.get(
            division, "You are J-BOT, the local J-ROC AI Desktop OS assistant."
        )
        body = json.dumps({
            "model": LOCAL_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_command},
            ],
            "stream": False,
        }).encode("utf-8")
        request = urllib.request.Request(
            OLLAMA_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            reply = data.get("message", {}).get("content")
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("Local model returned an empty response")
            elapsed = int((time.monotonic() - started) * 1000)
            self._log(LOCAL_MODEL, division, elapsed, 1)
            return {
                "status": "OK",
                "model": LOCAL_MODEL,
                "latency_ms": elapsed,
                "output": reply,
            }
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            elapsed = int((time.monotonic() - started) * 1000)
            self._log(LOCAL_MODEL, division, elapsed, 0)
            return {
                "status": "LOCAL_OFFLINE",
                "model": LOCAL_MODEL,
                "latency_ms": elapsed,
                "output": (
                    f"Local inference is unavailable ({exc}). No hosted AI service was contacted. "
                    "Start the approved local Ollama model and retry."
                ),
            }

    def _log(self, model, division, latency_ms, success):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO model_telemetry (model_used, division, latency_ms, success, timestamp) VALUES (?, ?, ?, ?, ?)",
            (model, division, latency_ms, success, datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
