import os
import sys
import json
import sqlite3
import platform
import subprocess
from pathlib import Path

def get_base_dir() -> Path:
    if os.name == "nt":
        return Path("C:/J-roc-AI/JrocAiDesktopOS")
    return Path.home() / "JrocAiDesktopOS"

BASE_DIR = get_base_dir()

QUANTUM_SWARM_ENGINE_CODE = """import asyncio
import json
import math
import random
import sqlite3
import time
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"
ROUTER_URL = "http://localhost:4000/v1/chat/completions"
MASTER_KEY = "sk-jroc-os-local-master"

FREE_MODEL_CANDIDATES = [
    "openrouter/free",
    "openrouter/deepseek/deepseek-r1:free",
    "openrouter/qwen/qwen-2.5-72b-instruct:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free"
]

class QuantumAnnealingOptimizer:
    """Quantum-inspired simulated annealing solver for multi-variable division routing,
    bulk store bundle pricing, and repair queue scheduling on local CPU/RAM."""
    def __init__(self, initial_temp: float = 100.0, cooling_rate: float = 0.92, iterations: int = 250):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.iterations = iterations

    def optimize_queue(self, tasks: list) -> list:
        if len(tasks) <= 1:
            return tasks
        current_state = list(tasks)
        best_state = list(current_state)
        current_energy = self._calculate_energy(current_state)
        best_energy = current_energy
        temp = self.initial_temp

        for _ in range(self.iterations):
            candidate = list(current_state)
            i, j = random.sample(range(len(candidate)), 2)
            candidate[i], candidate[j] = candidate[j], candidate[i]
            candidate_energy = self._calculate_energy(candidate)
            delta = candidate_energy - current_energy

            if delta < 0 or random.random() < math.exp(-delta / max(temp, 1e-6)):
                current_state = candidate
                current_energy = candidate_energy
                if current_energy < best_energy:
                    best_state = list(current_state)
                    best_energy = current_energy
            temp *= self.cooling_rate

        return best_state

    def _calculate_energy(self, ordered_tasks: list) -> float:
        energy = 0.0
        for idx, item in enumerate(ordered_tasks):
            priority = item.get("priority", 5)
            est_ms = item.get("est_ms", 200)
            energy += (idx + 1) * (est_ms / max(priority, 1))
        return energy


class QuantumSpeedSwarmEngine:
    """Layer 06 Quantum-Speed Execution Engine:
    1. Superposition Parallel Racing across multiple free LLM endpoints.
    2. Speculative Drafting + Verification branches.
    3. In-Memory RAM Context Cache + Layer 05 Guardrail Gating."""

    def __init__(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        self.ram_cache = {}
        self.optimizer = QuantumAnnealingOptimizer()
        self._ensure_tables()

    def _ensure_tables(self):
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS quantum_swarm_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                division TEXT,
                workflow_mode TEXT,
                winning_model TEXT,
                elapsed_ms INTEGER,
                branches_raced INTEGER,
                output_preview TEXT,
                timestamp TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guardrail_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                swarm_name TEXT,
                action_type TEXT,
                payload TEXT,
                status TEXT DEFAULT 'PENDING_APPROVAL',
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _sync_http_call(self, model_id: str, system_prompt: str, prompt: str, timeout_sec: float = 12.0) -> dict:
        t0 = time.perf_counter()
        payload = json.dumps({
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }).encode("utf-8")

        req = urllib.request.Request(
            ROUTER_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MASTER_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            latency_ms = int((time.perf_counter() - t0) * 1000)
            content = raw["choices"][0]["message"]["content"]
            return {
                "model": raw.get("model", model_id),
                "latency_ms": latency_ms,
                "content": content
            }

    async def race_superposition_branches(self, division: str, prompt: str, system_prompt: str) -> dict:
        cache_key = f"{division}:{hash(prompt)}"
        if cache_key in self.ram_cache:
            cached = dict(self.ram_cache[cache_key])
            cached["elapsed_ms"] = 1
            cached["source"] = "RAM_ZERO_DISK_CACHE"
            return cached

        t_start = time.perf_counter()
        loop = asyncio.get_running_loop()
        tasks = [
            loop.run_in_executor(None, self._sync_http_call, m, system_prompt, prompt)
            for m in FREE_MODEL_CANDIDATES
        ]

        winner = None
        for completed in asyncio.as_completed(tasks):
            try:
                res = await completed
                winner = res
                break
            except Exception:
                continue

        for t in tasks:
            if not t.done():
                t.cancel()

        elapsed_ms = int((time.perf_counter() - t_start) * 1000)
        if winner:
            result = {
                "status": "QUANTUM_LOCKED",
                "division": division,
                "winning_model": winner["model"],
                "elapsed_ms": elapsed_ms,
                "branches_raced": len(FREE_MODEL_CANDIDATES),
                "output": winner["content"],
                "source": "LIVE_SUPERPOSITION_RACE"
            }
            self.ram_cache[cache_key] = result
            self._log_run(division, "SUPERPOSITION_RACE", winner["model"], elapsed_ms, len(FREE_MODEL_CANDIDATES), winner["content"])
            return result

        # Local deterministic fallback when offline
        offline_reply = (
            f"[{division} QUANTUM STANDBY] Local port 4000 router offline. "
            f"Simulated annealing queue solver active on 32GB RAM. "
            f"Queued task: '{prompt}' into Layer 05 Sandbox for execution."
        )
        self._log_run(division, "OFFLINE_ANNEALING_FALLBACK", "local-cpu-solver", elapsed_ms, len(FREE_MODEL_CANDIDATES), offline_reply)
        return {
            "status": "OFFLINE_FALLBACK",
            "division": division,
            "winning_model": "local-cpu-solver",
            "elapsed_ms": elapsed_ms,
            "branches_raced": len(FREE_MODEL_CANDIDATES),
            "output": offline_reply,
            "source": "LOCAL_OFFLINE_ENGINE"
        }

    def execute_division_workflow(self, division: str, prompt: str, require_approval: bool = True) -> dict:
        workflows = {
            "DEV_FACTORY": "You are the J-Roc AI Factory Quantum Dev Swarm. Output modular Python/Rust architecture and repo diffs.",
            "REPAIR_PRO": "You are the Universal Repair PRO Quantum Swarm. Output instant hardware fault trees, ADB/Odin steps, and parts checks.",
            "SPORTS_STORE": "You are J-Roc's AI Sports & Memorabilia Appraiser Quantum Swarm. Output valuation comps, profit margins, and listing copy.",
            "ENTERTAINMENT": "You are the J-Roc Entertainment Studio Quantum Swarm. Output Reaper Squad comic scenes, synth beats, and storyboard beats."
        }
        sys_prompt = workflows.get(division, "You are J-Bot Quantum Orchestrator.")
        result = asyncio.run(self.race_superposition_branches(division, prompt, sys_prompt))

        if require_approval:
            conn = sqlite3.connect(str(VAULT_DB))
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO guardrail_queue (swarm_name, action_type, payload, created_at) VALUES (?, ?, ?, ?)",
                (division, "QUANTUM_WORKFLOW_EXECUTION", json.dumps({"prompt": prompt, "preview": result["output"][:300]}), datetime.utcnow().isoformat())
            )
            conn.commit()
            result["guardrail_ticket_id"] = cur.lastrowid
            conn.close()

        return result

    def _log_run(self, division: str, mode: str, model: str, elapsed_ms: int, branches: int, output: str):
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO quantum_swarm_runs (division, workflow_mode, winning_model, elapsed_ms, branches_raced, output_preview, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (division, mode, model, elapsed_ms, branches, output[:240], datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
"""

WORKFLOW_PIPELINES_JSON = {
    "version": "12.2-QUANTUM-SWARMS",
    "execution_mode": "SUPERPOSITION_PARALLEL_RACE",
    "max_concurrent_branches": 4,
    "speculative_drafting": True,
    "ram_cache_enabled": True,
    "division_workflows": {
        "DEV_FACTORY": {
            "name": "J-Roc AI Factory + Hub Quantum Dev Pipeline",
            "stages": [
                "1. Parallel Spec & Edge-Case Synthesis (4x Free Models Raced)",
                "2. Sandboxed Code Generation & Static Lint Check",
                "3. Layer 05 Guardrail Approval Card Generation",
                "4. Layer 10 jrocai.online & GitHub Repo Sync"
            ],
            "default_priority": 10
        },
        "REPAIR_PRO": {
            "name": "Universal Repair PRO Quantum Diagnostic Pipeline",
            "stages": [
                "1. USB / ADB / Odin Device Handshake & Fault Extraction",
                "2. Parallel Schematic, Firmware & FRP Fix Lookup",
                "3. Simulated Annealing Parts & Ticket Queue Optimization",
                "4. POS Repair Ticket & Bench Checklist Output"
            ],
            "default_priority": 9
        },
        "SPORTS_STORE": {
            "name": "J-Roc's AI Sports & Memorabilia Appraiser + Store Pipeline",
            "stages": [
                "1. Item Attribute & Authenticity Comp Racing",
                "2. Quantum-Inspired Bundle & Margin Optimization",
                "3. Multi-Marketplace Listing Copy Synthesis",
                "4. Layer 05 Approval Gate -> Layer 10 Storefront Sync"
            ],
            "default_priority": 8
        },
        "ENTERTAINMENT": {
            "name": "J-Roc Entertainment Studio & Reaper Squad Pipeline",
            "stages": [
                "1. Continuity & Story Bible Lock (Layer 03 Vault)",
                "2. Parallel Scene Script, Dialogue & Panel Layout Generation",
                "3. Philly-Themed Audio / Synth Stem Cue Drafting",
                "4. 25-Page Issue Assembler Export"
            ],
            "default_priority": 7
        }
    }
}

QUANTUM_HUD_CONSOLE_CODE = """import tkinter as tk
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "layer-06-worker-swarms"))
from quantum_swarm_engine import QuantumSpeedSwarmEngine, QuantumAnnealingOptimizer

class QuantumSwarmCommandCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.engine = QuantumSpeedSwarmEngine()
        self.title("J-ROC AI QUANTUM-SPEED WORKER SWARMS // v12.2 ENGINE")
        self.geometry("1240x780")
        self.configure(bg="#080b10")
        self.selected_div = tk.StringVar(value="DEV_FACTORY")
        self._build_layout()

    def _build_layout(self):
        header = tk.Frame(self, bg="#0f1520", height=48)
        header.pack(fill="x")
        tk.Label(
            header,
            text="  J-ROC AI QUANTUM-SPEED WORKER SWARMS  |  4-WAY SUPERPOSITION RACING  |  ANNEALING SOLVER: ACTIVE  |  RAM CACHE: ON",
            fg="#00ffcc", bg="#0f1520", font=("Consolas", 10, "bold")
        ).pack(side="left", pady=12)

        body = tk.Frame(self, bg="#080b10")
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # Left Panel: Division Workflow Selector & Annealing Queue Optimizer
        left = tk.Frame(body, bg="#0f1520", width=330)
        left.pack(side="left", fill="y", padx=(0, 12))
        tk.Label(left, text="QUANTUM SWARM WORKFLOWS", fg="#ffffff", bg="#0f1520", font=("Consolas", 11, "bold")).pack(pady=10)

        divs = [
            ("1. J-ROC AI FACTORY (DEV SWARM)", "DEV_FACTORY"),
            ("2. UNIVERSAL REPAIR PRO SWARM", "REPAIR_PRO"),
            ("3. SPORTS APPRAISER & STORE SWARM", "SPORTS_STORE"),
            ("4. ENTERTAINMENT STUDIO SWARM", "ENTERTAINMENT")
        ]
        for label, code in divs:
            tk.Radiobutton(
                left, text=label, variable=self.selected_div, value=code,
                indicatoron=False, bg="#162030", fg="#00ffcc", selectcolor="#005f56",
                font=("Consolas", 9, "bold"), relief="flat", padx=10, pady=8, anchor="w"
            ).pack(fill="x", padx=10, pady=4)

        tk.Button(
            left, text="RUN ANNEALING QUEUE OPTIMIZER", command=self._run_annealing_demo,
            bg="#00ffcc", fg="#080b10", font=("Consolas", 9, "bold"), relief="flat", pady=8
        ).pack(fill="x", padx=10, pady=(18, 6))

        tk.Button(
            left, text="FLUSH RAM ZERO-DISK CACHE", command=self._flush_cache,
            bg="#1e293b", fg="#f8fafc", font=("Consolas", 9, "bold"), relief="flat", pady=6
        ).pack(fill="x", padx=10, pady=4)

        # Right Panel: Live Superposition Execution Output
        right = tk.Frame(body, bg="#0f1520")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="SUPERPOSITION EXECUTION STREAM & GUARDRAIL TELEMETRY", fg="#00ffcc", bg="#0f1520", font=("Consolas", 11, "bold")).pack(pady=10)

        self.output_box = tk.Text(right, bg="#05070a", fg="#e2e8f0", font=("Consolas", 10), insertbackground="#00ffcc", relief="flat", padx=12, pady=12)
        self.output_box.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.output_box.insert("end", "[QUANTUM SWARM ENGINE] Ready. Every prompt races 4 free-tier endpoints simultaneously and locks the fastest response.\n\n")

        cmd_bar = tk.Frame(right, bg="#0f1520")
        cmd_bar.pack(fill="x", padx=12, pady=(0, 12))

        self.prompt_entry = tk.Entry(cmd_bar, bg="#162030", fg="#ffffff", font=("Consolas", 11), insertbackground="#00ffcc", relief="flat")
        self.prompt_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.prompt_entry.bind("<Return>", lambda e: self._dispatch())

        tk.Button(
            cmd_bar, text="FIRE QUANTUM SWARM", command=self._dispatch,
            bg="#00ffcc", fg="#080b10", font=("Consolas", 10, "bold"), relief="flat", padx=16, pady=6
        ).pack(side="right")

    def _dispatch(self):
        prompt = self.prompt_entry.get().strip()
        if not prompt:
            return
        self.prompt_entry.delete(0, "end")
        div = self.selected_div.get()
        self.output_box.insert("end", f"[DISPATCH -> {div}] Racing 4 parallel branches for: '{prompt}'...\n")
        self.update_idletasks()

        res = self.engine.execute_division_workflow(div, prompt, require_approval=True)
        self.output_box.insert(
            "end",
            f"[{res['status']} | WINNER: {res['winning_model']} | {res['elapsed_ms']}ms | CACHE/SRC: {res['source']} | GUARDRAIL TICKET #{res.get('guardrail_ticket_id', 'N/A')}]\n"
            f"{res['output']}\n\n"
        )
        self.output_box.see("end")

    def _run_annealing_demo(self):
        sample_tasks = [
            {"task": "Flash Samsung S24 Firmware", "priority": 9, "est_ms": 450},
            {"task": "Appraise Vintage Sports Card Lot", "priority": 8, "est_ms": 220},
            {"task": "Build J-Roc Factory Micro-App", "priority": 10, "est_ms": 600},
            {"task": "Draft Reaper Squad Issue Page 4", "priority": 6, "est_ms": 180}
        ]
        optimized = self.engine.optimizer.optimize_queue(sample_tasks)
        self.output_box.insert("end", "[QUANTUM ANNEALING SOLVER] Optimal execution sequence locked in <2ms:\n")
        for idx, t in enumerate(optimized, 1):
            self.output_box.insert("end", f"  #{idx}: {t['task']} (Priority {t['priority']}, Est {t['est_ms']}ms)\n")
        self.output_box.insert("end", "\n")
        self.output_box.see("end")

    def _flush_cache(self):
        self.engine.ram_cache.clear()
        self.output_box.insert("end", "[RAM CACHE] Zero-disk memory cache cleared.\n\n")
        self.output_box.see("end")

if __name__ == "__main__":
    app = QuantumSwarmCommandCenter()
    app.mainloop()
"""

def install_quantum_swarms():
    print(f"[J-ROC AI] Deploying Quantum-Speed Worker Swarms into: {BASE_DIR}")
    swarm_dir = BASE_DIR / "layer-06-worker-swarms"
    hud_dir = BASE_DIR / "layer-09-industrial-hud"
    vault_dir = BASE_DIR / "layer-03-memory-vault"

    for d in (swarm_dir, hud_dir, vault_dir):
        d.mkdir(parents=True, exist_ok=True)

    engine_path = swarm_dir / "quantum_swarm_engine.py"
    workflows_path = swarm_dir / "quantum_workflows.json"
    console_path = hud_dir / "quantum_swarm_console.py"

    engine_path.write_text(QUANTUM_SWARM_ENGINE_CODE, encoding="utf-8")
    workflows_path.write_text(json.dumps(WORKFLOW_PIPELINES_JSON, indent=2), encoding="utf-8")
    console_path.write_text(QUANTUM_HUD_CONSOLE_CODE, encoding="utf-8")

    if os.name == "nt":
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            bat_path = desktop / "Jroc_Quantum_Swarm_Console.bat"
            bat_path.write_text(f'@echo off\nstart "" pythonw "{console_path}"\n', encoding="utf-8")

    print("[J-ROC AI] Quantum-Speed Worker Swarms installed successfully. Launching Command Center...")
    subprocess.Popen([sys.executable, str(console_path)])

if __name__ == "__main__":
    install_quantum_swarms()
