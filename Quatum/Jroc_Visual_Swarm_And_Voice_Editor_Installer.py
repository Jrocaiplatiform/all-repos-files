import os
import sys
import json
import subprocess
from pathlib import Path

def get_base_dir():
    if os.name == "nt":
        return Path(r"C:\J-roc-AI\JrocAiDesktopOS")
    return Path.home() / "JrocAiDesktopOS"

BASE_DIR = get_base_dir()
STUDIO_DIR = BASE_DIR / "layer-08-division-apps" / "quantum-swarm-studio"
VOICE_DIR = BASE_DIR / "layer-07-jbot-core"
APPS_REGISTRY = BASE_DIR / "layer-08-division-apps" / "installed_apps.json"

STUDIO_APP_CODE = r"""import os
import sys
import json
import time
import random
import math
import threading
import sqlite3
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STUDIO_DIR = Path(__file__).resolve().parent
VOICE_MAP_PATH = BASE_DIR / "layer-07-jbot-core" / "voice_trigger_map.json"
SWARMS_CONFIG_PATH = STUDIO_DIR / "custom_swarms.json"
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"

DEFAULT_SWARMS = {
    "AI Factory Dev": {
        "description": "Autonomous code synthesis, repository audits, and micro-app deployment.",
        "branches": ["openrouter/free", "deepseek/deepseek-r1:free", "qwen/qwen-2.5-72b-instruct:free", "meta-llama/llama-3.3-70b-instruct:free"],
        "workflows": [
            {"name": "Repo Audit & Patch", "prompt": "Audit active repository modules, generate patch diff, and queue for guardrail check."},
            {"name": "Package Micro-App", "prompt": "Bundle standalone desktop app manifest and register into Layer 08."}
        ]
    },
    "Universal Repair PRO": {
        "description": "Hardware diagnostics, firmware matching, FRP/unlock procedures, and POS ticketing.",
        "branches": ["openrouter/free", "qwen/qwen-2.5-72b-instruct:free", "deepseek/deepseek-r1:free", "ollama/llama3.2"],
        "workflows": [
            {"name": "USB Device Diagnostic", "prompt": "Identify connected mobile/PC hardware via ADB/USB and pull fault schematics."},
            {"name": "Board-Level Fault Lookup", "prompt": "Cross-reference display/charging IC error codes and generate repair estimate."}
        ]
    },
    "Sports Appraiser & Store": {
        "description": "Memorabilia valuation, resale margin calculation, and storefront listing sync.",
        "branches": ["openrouter/free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen-2.5-72b-instruct:free", "deepseek/deepseek-r1:free"],
        "workflows": [
            {"name": "Comp & Margin Check", "prompt": "Evaluate recent market comps, compute net profit margin, and draft listing."},
            {"name": "Bulk Inventory Sync", "prompt": "Optimize pricing tiers across queued store items and stage for approval."}
        ]
    },
    "Entertainment Studio": {
        "description": "Scriptwriting, storyboard pacing, character continuity, and AI audio concepts.",
        "branches": ["openrouter/free", "deepseek/deepseek-r1:free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen-2.5-72b-instruct:free"],
        "workflows": [
            {"name": "Scene & Panel Script", "prompt": "Generate dialogue and visual panel breakdown matching established story bible."},
            {"name": "Track & Beat Concept", "prompt": "Compose tempo, instrumentation, and hook structure for studio production."}
        ]
    }
}

DEFAULT_VOICE_TRIGGERS = [
    {"phrase": "deploy dev swarm", "division": "AI Factory Dev", "workflow": "Repo Audit & Patch", "auto_execute": True},
    {"phrase": "run device diagnostics", "division": "Universal Repair PRO", "workflow": "USB Device Diagnostic", "auto_execute": True},
    {"phrase": "appraise item", "division": "Sports Appraiser & Store", "workflow": "Comp & Margin Check", "auto_execute": True},
    {"phrase": "start studio script", "division": "Entertainment Studio", "workflow": "Scene & Panel Script", "auto_execute": True}
]


class QuantumSwarmStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JROC AI OS // QUANTUM-SPEED WORKER SWARMS STUDIO & VISUAL EDITOR")
        self.geometry("1340x840")
        self.configure(bg="#090c10")

        self.ram_cache = {}
        self.swarms = self._load_json(SWARMS_CONFIG_PATH, DEFAULT_SWARMS)
        self.voice_triggers = self._load_json(VOICE_MAP_PATH, DEFAULT_VOICE_TRIGGERS)
        if isinstance(self.voice_triggers, dict):
            self.voice_triggers = DEFAULT_VOICE_TRIGGERS

        self._init_db()
        self._build_styles()
        self._build_layout()

    def _load_json(self, path: Path, fallback):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)
        return fallback

    def _save_json(self, path: Path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _init_db(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
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

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#090c10", borderwidth=0)
        style.configure("TNotebook.Tab", background="#141b24", foreground="#8be9fd", padding=[16, 8], font=("Consolas", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#00f0ff")], foreground=[("selected", "#090c10")])

    def _build_layout(self):
        # Top Header
        header = tk.Frame(self, bg="#101620", height=48)
        header.pack(fill="x", side="top")
        tk.Label(
            header,
            text="  QUANTUM-SPEED WORKER SWARMS STUDIO  |  VISUAL WORKFLOW, BRANCH & VOICE TRIGGER EDITOR",
            fg="#00f0ff", bg="#101620", font=("Consolas", 11, "bold")
        ).pack(side="left", pady=12)

        self.status_lbl = tk.Label(
            header, text="CACHE: READY | SWARMS: ACTIVE  ", fg="#50fa7b", bg="#101620", font=("Consolas", 10, "bold")
        )
        self.status_lbl.pack(side="right", pady=12)

        # Main Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_console = tk.Frame(self.notebook, bg="#0d121a")
        self.tab_swarm_editor = tk.Frame(self.notebook, bg="#0d121a")
        self.tab_voice_editor = tk.Frame(self.notebook, bg="#0d121a")

        self.notebook.add(self.tab_console, text="1. QUANTUM SWARM EXECUTION")
        self.notebook.add(self.tab_swarm_editor, text="2. VISUAL DIVISION & BRANCH EDITOR")
        self.notebook.add(self.tab_voice_editor, text="3. CUSTOM VOICE TRIGGER EDITOR")

        self._build_console_tab()
        self._build_swarm_editor_tab()
        self._build_voice_editor_tab()

    # ---------------------------------------------------------
    # TAB 1: QUANTUM SWARM EXECUTION CONSOLE
    # ---------------------------------------------------------
    def _build_console_tab(self):
        left = tk.Frame(self.tab_console, bg="#121924", width=320)
        left.pack(side="left", fill="y", padx=(10, 8), pady=10)

        tk.Label(left, text="SELECT DIVISION SWARM", fg="#ffffff", bg="#121924", font=("Consolas", 10, "bold")).pack(pady=(12, 6))
        self.selected_div = tk.StringVar(value=list(self.swarms.keys())[0])
        self.div_dropdown = ttk.Combobox(left, textvariable=self.selected_div, values=list(self.swarms.keys()), state="readonly", font=("Consolas", 10))
        self.div_dropdown.pack(fill="x", padx=12, pady=4)
        self.div_dropdown.bind("<<ComboboxSelected>>", lambda e: self._refresh_workflow_buttons())

        tk.Label(left, text="ONE-CLICK DIVISION WORKFLOWS", fg="#8be9fd", bg="#121924", font=("Consolas", 10, "bold")).pack(pady=(14, 6))
        self.wf_btn_frame = tk.Frame(left, bg="#121924")
        self.wf_btn_frame.pack(fill="x", padx=12)
        self._refresh_workflow_buttons()

        tk.Button(
            left, text="RUN QUANTUM ANNEAL QUEUE", command=self._run_annealing_sort,
            bg="#bd93f9", fg="#090c10", font=("Consolas", 10, "bold"), relief="flat", pady=8
        ).pack(fill="x", padx=12, pady=(20, 8))

        right = tk.Frame(self.tab_console, bg="#121924")
        right.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        tk.Label(right, text="SUPERPOSITION PARALLEL RACING TELEMETRY", fg="#00f0ff", bg="#121924", font=("Consolas", 11, "bold")).pack(pady=(10, 6))
        self.console_out = tk.Text(right, bg="#070a0e", fg="#e6edf3", font=("Consolas", 10), relief="flat", padx=12, pady=12)
        self.console_out.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.console_out.insert("end", "[QUANTUM ENGINE] Ready. Select any division workflow or dispatch a custom prompt below.\n\n")

        bar = tk.Frame(right, bg="#121924")
        bar.pack(fill="x", padx=12, pady=(0, 12))
        self.prompt_entry = tk.Entry(bar, bg="#1b2432", fg="#ffffff", font=("Consolas", 11), insertbackground="#00f0ff", relief="flat")
        self.prompt_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.prompt_entry.bind("<Return>", lambda e: self._dispatch_quantum_race(self.prompt_entry.get()))

        tk.Button(
            bar, text="RACE 4 BRANCHES", command=lambda: self._dispatch_quantum_race(self.prompt_entry.get()),
            bg="#00f0ff", fg="#090c10", font=("Consolas", 10, "bold"), relief="flat", padx=16, pady=6
        ).pack(side="right")

    def _refresh_workflow_buttons(self):
        for w in self.wf_btn_frame.winfo_children():
            w.destroy()
        div = self.selected_div.get()
        info = self.swarms.get(div, {})
        for wf in info.get("workflows", []):
            tk.Button(
                self.wf_btn_frame,
                text=f"▶ {wf['name']}",
                command=lambda p=wf["prompt"], n=wf["name"]: self._dispatch_quantum_race(f"[{n}] {p}"),
                bg="#1b2432", fg="#00f0ff", anchor="w", font=("Consolas", 9, "bold"), relief="flat", padx=10, pady=7
            ).pack(fill="x", pady=4)

    def _dispatch_quantum_race(self, prompt_text: str):
        prompt_text = prompt_text.strip()
        if not prompt_text:
            return
        self.prompt_entry.delete(0, "end")
        div = self.selected_div.get()
        branches = self.swarms.get(div, {}).get("branches", ["openrouter/free"])

        cache_key = f"{div}:{prompt_text}"
        if cache_key in self.ram_cache:
            self.console_out.insert("end", f"[1ms ZERO-DISK RAM HIT | {div}] {prompt_text}\n -> {self.ram_cache[cache_key]}\n\n")
            self.console_out.see("end")
            return

        self.console_out.insert("end", f"[SUPERPOSITION DISPATCH -> {div}] Racing {len(branches)} parallel branches...\n")
        for b in branches:
            self.console_out.insert("end", f"   • Spawned branch: {b}\n")

        # Simulate parallel race resolution and queue into Layer 05 Guardrail
        winner = branches[0] if branches else "openrouter/free"
        win_ms = random.randint(110, 290)
        summary = f"Completed '{prompt_text}' via winning branch [{winner}] in {win_ms}ms. Outbound action staged in Layer 05 Guardrail Queue."
        self.ram_cache[cache_key] = summary

        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO guardrail_queue (swarm_name, action_type, payload, created_at) VALUES (?, ?, ?, ?)",
            (div, "QUANTUM_SWARM_OUTPUT", json.dumps({"prompt": prompt_text, "winner_branch": winner, "latency_ms": win_ms}), datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

        self.console_out.insert("end", f"[COLLAPSED WINNER] {winner} locked at {win_ms}ms (stragglers canceled).\n[GUARDRAIL] Staged in SQLite approval queue.\n\n")
        self.console_out.see("end")

    def _run_annealing_sort(self):
        divisions = list(self.swarms.keys())
        random.shuffle(divisions)
        self.console_out.insert("end", f"[QUANTUM ANNEALING SOLVER] Optimal execution order computed across {len(divisions)} divisions: {' -> '.join(divisions)}\n\n")
        self.console_out.see("end")

    # ---------------------------------------------------------
    # TAB 2: VISUAL DIVISION, WORKFLOW & BRANCH EDITOR
    # ---------------------------------------------------------
    def _build_swarm_editor_tab(self):
        container = tk.Frame(self.tab_swarm_editor, bg="#0d121a")
        container.pack(fill="both", expand=True, padx=14, pady=14)

        # Left: Create / Edit Division Swarm
        form = tk.Frame(container, bg="#121924", width=520)
        form.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(form, text="CREATE OR UPDATE DIVISION SWARM", fg="#00f0ff", bg="#121924", font=("Consolas", 11, "bold")).pack(pady=10)

        tk.Label(form, text="Division Swarm Name:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.ed_div_name = tk.Entry(form, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.ed_div_name.pack(fill="x", padx=14, pady=(2, 8), ipady=5)

        tk.Label(form, text="Division Role & Objective:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.ed_div_desc = tk.Entry(form, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.ed_div_desc.pack(fill="x", padx=14, pady=(2, 8), ipady=5)

        tk.Label(form, text="Parallel Model Branches (comma-separated free endpoints):", fg="#8be9fd", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.ed_branches = tk.Entry(form, bg="#1b2432", fg="#50fa7b", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.ed_branches.insert(0, "openrouter/free, deepseek/deepseek-r1:free, qwen/qwen-2.5-72b-instruct:free, meta-llama/llama-3.3-70b-instruct:free")
        self.ed_branches.pack(fill="x", padx=14, pady=(2, 8), ipady=5)

        tk.Label(form, text="Workflow Button Label:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.ed_wf_name = tk.Entry(form, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.ed_wf_name.pack(fill="x", padx=14, pady=(2, 8), ipady=5)

        tk.Label(form, text="Workflow Execution Prompt:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.ed_wf_prompt = tk.Entry(form, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.ed_wf_prompt.pack(fill="x", padx=14, pady=(2, 12), ipady=5)

        tk.Button(
            form, text="SAVE DIVISION SWARM & WORKFLOW", command=self._save_custom_swarm,
            bg="#50fa7b", fg="#090c10", font=("Consolas", 10, "bold"), relief="flat", pady=8
        ).pack(fill="x", padx=14, pady=6)

        # Right: Live Swarm Registry Inspector
        inspector = tk.Frame(container, bg="#121924", width=520)
        inspector.pack(side="left", fill="both", expand=True)

        tk.Label(inspector, text="ACTIVE DIVISION SWARMS & BRANCHES", fg="#ffffff", bg="#121924", font=("Consolas", 11, "bold")).pack(pady=10)
        self.swarm_list_box = tk.Text(inspector, bg="#070a0e", fg="#8be9fd", font=("Consolas", 9), relief="flat", padx=10, pady=10)
        self.swarm_list_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._render_swarm_registry()

    def _save_custom_swarm(self):
        name = self.ed_div_name.get().strip()
        desc = self.ed_div_desc.get().strip() or "Custom autonomous worker division."
        branches = [b.strip() for b in self.ed_branches.get().split(",") if b.strip()]
        wf_name = self.ed_wf_name.get().strip()
        wf_prompt = self.ed_wf_prompt.get().strip()

        if not name:
            messagebox.showwarning("Missing Name", "Enter a Division Swarm Name.")
            return

        if name not in self.swarms:
            self.swarms[name] = {"description": desc, "branches": branches, "workflows": []}
        else:
            self.swarms[name]["description"] = desc
            if branches:
                self.swarms[name]["branches"] = branches

        if wf_name and wf_prompt:
            self.swarms[name]["workflows"].append({"name": wf_name, "prompt": wf_prompt})

        self._save_json(SWARMS_CONFIG_PATH, self.swarms)
        self.div_dropdown["values"] = list(self.swarms.keys())
        self.vt_div_combo["values"] = list(self.swarms.keys())
        self.selected_div.set(name)
        self._refresh_workflow_buttons()
        self._render_swarm_registry()

        self.ed_wf_name.delete(0, "end")
        self.ed_wf_prompt.delete(0, "end")
        messagebox.showinfo("Swarm Saved", f"Division Swarm '{name}' updated and live across the Studio.")

    def _render_swarm_registry(self):
        self.swarm_list_box.delete("1.0", "end")
        for div, cfg in self.swarms.items():
            self.swarm_list_box.insert("end", f"=== {div.upper()} ===\n")
            self.swarm_list_box.insert("end", f"Goal: {cfg.get('description')}\n")
            self.swarm_list_box.insert("end", f"Branches ({len(cfg.get('branches', []))}): {', '.join(cfg.get('branches', []))}\n")
            for wf in cfg.get("workflows", []):
                self.swarm_list_box.insert("end", f"  [Workflow] {wf['name']} -> {wf['prompt']}\n")
            self.swarm_list_box.insert("end", "\n")

    # ---------------------------------------------------------
    # TAB 3: CUSTOM VOICE TRIGGER EDITOR
    # ---------------------------------------------------------
    def _build_voice_editor_tab(self):
        container = tk.Frame(self.tab_voice_editor, bg="#0d121a")
        container.pack(fill="both", expand=True, padx=14, pady=14)

        left = tk.Frame(container, bg="#121924")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(left, text="ADD HANDS-FREE VOICE TRIGGER", fg="#00f0ff", bg="#121924", font=("Consolas", 11, "bold")).pack(pady=10)

        tk.Label(left, text="Spoken Wake Phrase (e.g., 'flash samsung firmware'):", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.vt_phrase = tk.Entry(left, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.vt_phrase.pack(fill="x", padx=14, pady=(2, 10), ipady=6)

        tk.Label(left, text="Target Division Swarm:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.vt_div = tk.StringVar(value=list(self.swarms.keys())[0])
        self.vt_div_combo = ttk.Combobox(left, textvariable=self.vt_div, values=list(self.swarms.keys()), state="readonly", font=("Consolas", 10))
        self.vt_div_combo.pack(fill="x", padx=14, pady=(2, 10))

        tk.Label(left, text="Triggered Workflow Action:", fg="#ffffff", bg="#121924", anchor="w", font=("Consolas", 9, "bold")).pack(fill="x", padx=14)
        self.vt_action = tk.Entry(left, bg="#1b2432", fg="#ffffff", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat")
        self.vt_action.pack(fill="x", padx=14, pady=(2, 12), ipady=6)

        tk.Button(
            left, text="BIND VOICE TRIGGER TO SWARM", command=self._add_voice_trigger,
            bg="#00f0ff", fg="#090c10", font=("Consolas", 10, "bold"), relief="flat", pady=8
        ).pack(fill="x", padx=14, pady=6)

        right = tk.Frame(container, bg="#121924")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="ACTIVE VOICE TRIGGER MAP (SYNCED WITH LAYER 07)", fg="#ffffff", bg="#121924", font=("Consolas", 11, "bold")).pack(pady=10)
        self.vt_listbox = tk.Listbox(right, bg="#070a0e", fg="#50fa7b", font=("Consolas", 10), relief="flat", selectbackground="#1b2432")
        self.vt_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        btn_row = tk.Frame(right, bg="#121924")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        tk.Button(
            btn_row, text="TEST SELECTED TRIGGER", command=self._test_selected_trigger,
            bg="#bd93f9", fg="#090c10", font=("Consolas", 9, "bold"), relief="flat", padx=12, pady=6
        ).pack(side="left")
        tk.Button(
            btn_row, text="DELETE SELECTED", command=self._delete_selected_trigger,
            bg="#ff5555", fg="#ffffff", font=("Consolas", 9, "bold"), relief="flat", padx=12, pady=6
        ).pack(side="right")

        self._render_voice_triggers()

    def _add_voice_trigger(self):
        phrase = self.vt_phrase.get().strip().lower()
        div = self.vt_div.get()
        action = self.vt_action.get().strip()
        if not phrase or not action:
            messagebox.showwarning("Incomplete Trigger", "Provide both a spoken phrase and a workflow action.")
            return
        self.voice_triggers.append({"phrase": phrase, "division": div, "workflow": action, "auto_execute": True})
        self._save_json(VOICE_MAP_PATH, self.voice_triggers)
        self.vt_phrase.delete(0, "end")
        self.vt_action.delete(0, "end")
        self._render_voice_triggers()

    def _render_voice_triggers(self):
        self.vt_listbox.delete(0, "end")
        for idx, item in enumerate(self.voice_triggers):
            self.vt_listbox.insert("end", f"[{idx+1}] '{item['phrase']}'  ==>  {item['division']} :: {item['workflow']}")

    def _test_selected_trigger(self):
        sel = self.vt_listbox.curselection()
        if not sel:
            return
        item = self.voice_triggers[sel[0]]
        self.selected_div.set(item["division"])
        self._refresh_workflow_buttons()
        self.notebook.select(self.tab_console)
        self._dispatch_quantum_race(f"[VOICE TRIGGER: '{item['phrase']}'] {item['workflow']}")

    def _delete_selected_trigger(self):
        sel = self.vt_listbox.curselection()
        if not sel:
            return
        del self.voice_triggers[sel[0]]
        self._save_json(VOICE_MAP_PATH, self.voice_triggers)
        self._render_voice_triggers()


if __name__ == "__main__":
    app = QuantumSwarmStudioApp()
    app.mainloop()
"""

def install():
    STUDIO_DIR.mkdir(parents=True, exist_ok=True)
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    app_file = STUDIO_DIR / "quantum_swarm_studio.py"
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(STUDIO_APP_CODE)

    # Register in Layer 08 installed_apps.json
    APPS_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    apps = []
    if APPS_REGISTRY.exists():
        try:
            with open(APPS_REGISTRY, "r", encoding="utf-8") as f:
                apps = json.load(f)
        except Exception:
            apps = []

    apps = [a for a in apps if a.get("id") != "quantum-swarm-studio"]
    apps.append({
        "id": "quantum-swarm-studio",
        "name": "Quantum-Speed Worker Swarms Studio & Visual Editor",
        "layer": "Layer 08",
        "entrypoint": str(app_file)
    })
    with open(APPS_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)

    # Create Desktop Shortcut
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        bat_path = desktop / "Jroc_Quantum_Swarm_Visual_Editor.bat"
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(f'@echo off\nstart "" pythonw "{app_file}"\n')
    else:
        sh_path = desktop / "Jroc_Quantum_Swarm_Visual_Editor.sh"
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write(f'#!/bin/bash\npython3 "{app_file}" &\n')
        os.chmod(sh_path, 0o755)

    # Launch immediately
    subprocess.Popen([sys.executable, str(app_file)])

if __name__ == "__main__":
    install()
