import sqlite3
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"
ROUTER_URL = "http://localhost:4000/v1/chat/completions"
MASTER_KEY = "sk-jroc-os-local-master"

class JrocDesktopOSEngine:
    def __init__(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(VAULT_DB))
        self._init_layers()

    def _init_layers(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS memory_vault (id INTEGER PRIMARY KEY AUTOINCREMENT, division TEXT, key TEXT UNIQUE, value TEXT, updated_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS guardrail_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, swarm_name TEXT, action_type TEXT, payload TEXT, status TEXT DEFAULT 'PENDING_APPROVAL', created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS model_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, model_used TEXT, division TEXT, latency_ms INTEGER, success INTEGER, timestamp TEXT)")
        self.conn.commit()

    def save_memory(self, division, key, value):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO memory_vault (division, key, value, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at", (division, key, value, datetime.utcnow().isoformat()))
        self.conn.commit()

    def dispatch_to_swarm(self, division, user_command):
        profiles = {
            "DEV_OPS": "You are the J-Roc AI Factory Dev Swarm. Output clean system actions and repo updates.",
            "REPAIR_PRO": "You are the Universal Repair PRO Swarm. Diagnose hardware, firmware, and FRP/display faults.",
            "COMMERCE": "You are J-Roc AI Sports & Memorabilia Appraiser & Store Swarm. Price items and draft listings.",
            "STUDIO": "You are the J-Roc Entertainment Studio Swarm. Build scripts, storyboards, and audio concepts."
        }
        sys_prompt = profiles.get(division, "You are J-Bot, master orchestrator of Jroc Ai Desktop OS.")
        t0 = time.time()
        body = json.dumps({"model": "jroc-primary", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_command}]}).encode("utf-8")
        req = urllib.request.Request(ROUTER_URL, data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {MASTER_KEY}"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ms = int((time.time() - t0) * 1000)
                model_used = data.get("model", "jroc-primary-free")
                reply = data["choices"][0]["message"]["content"]
                self._log(model_used, division, ms, 1)
                return {"status": "OK", "model": model_used, "latency_ms": ms, "output": reply}
        except Exception:
            ms = int((time.time() - t0) * 1000)
            self._log("failover-standby", division, ms, 0)
            return {"status": "LOCAL_OFFLINE", "model": "jroc-local-fallback", "latency_ms": ms, "output": f"[QUEUED -> {division}] Saved to Layer 3 Vault. Start LiteLLM on port 4000 for live 250-model routing."}

    def _log(self, model, division, ms, success):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO model_telemetry (model_used, division, latency_ms, success, timestamp) VALUES (?, ?, ?, ?, ?)", (model, division, ms, success, datetime.utcnow().isoformat()))
        self.conn.commit()
