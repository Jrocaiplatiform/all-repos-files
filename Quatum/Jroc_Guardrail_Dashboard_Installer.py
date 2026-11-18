#!/usr/bin/env python3
"""
Jroc Ai Desktop OS - Layer 05 Real-Time SQLite Guardrail Approval Dashboard Installer
Builds and launches a native dark-mode approval dashboard wired to jroc_os_vault.db
with one-click + voice approval support and zero HTML pages.
"""

import os
import sys
import json
import sqlite3
import platform
import subprocess
from pathlib import Path

def get_base_dir() -> Path:
    if platform.system() == "Windows":
        return Path("C:/J-roc-AI/JrocAiDesktopOS")
    return Path.home() / "JrocAiDesktopOS"

GUARDRAIL_DASHBOARD_CODE = """#!/usr/bin/env python3
import sqlite3
import json
import threading
import subprocess
import platform
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_DB = BASE_DIR / "layer-03-memory-vault" / "jroc_os_vault.db"
OUTBOUND_LOG = BASE_DIR / "layer-10-revenue-sync" / "approved_outbound_actions.jsonl"


def speak_status(text: str):
    def _run():
        try:
            if platform.system() == "Windows":
                safe = text.replace("'", " ")
                cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe}')"
                subprocess.run(["powershell", "-WindowStyle", "Hidden", "-Command", cmd], check=False)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


class GuardrailApprovalDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JROC AI DESKTOP OS // LAYER 05 REAL-TIME GUARDRAIL APPROVAL DASHBOARD")
        self.geometry("1240x760")
        self.configure(bg="#090c10")
        self.selected_id = None
        self._ensure_db()
        self._build_ui()
        self._refresh_queue()
        self._auto_poll()

    def _ensure_db(self):
        VAULT_DB.parent.mkdir(parents=True, exist_ok=True)
        OUTBOUND_LOG.parent.mkdir(parents=True, exist_ok=True)
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
        cur.execute("SELECT COUNT(*) FROM guardrail_queue")
        if cur.fetchone()[0] == 0:
            samples = [
                ("COMMERCE_SWARM", "PUBLISH_LISTING", json.dumps({
                    "target": "jrocai.online / Storefront",
                    "item": "Vintage Graded Sports Card Lot #104",
                    "suggested_price": "$145.00",
                    "confidence": "98.4%"
                }), "PENDING_APPROVAL", datetime.utcnow().isoformat()),
                ("DEV_OPS_SWARM", "REPO_COMMIT_SYNC", json.dumps({
                    "repo": "Jrocai1/Jrocai.online",
                    "branch": "quantum-swarm-v12",
                    "files_changed": 3,
                    "risk_level": "LOW"
                }), "PENDING_APPROVAL", datetime.utcnow().isoformat()),
                ("REPAIR_PRO_SWARM", "FIRMWARE_FLASH_PACKAGE", json.dumps({
                    "device": "Android USB Unit (ADB-09)",
                    "action": "Stage Verified Diagnostics Profile",
                    "sandbox_verified": True
                }), "PENDING_APPROVAL", datetime.utcnow().isoformat())
            ]
            cur.executemany(
                "INSERT INTO guardrail_queue (swarm_name, action_type, payload, status, created_at) VALUES (?, ?, ?, ?, ?)",
                samples
            )
        conn.commit()
        conn.close()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0f141c", foreground="#e6edf3", fieldbackground="#0f141c", rowheight=32, font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#161e2b", foreground="#00f0ff", font=("Consolas", 10, "bold"))
        style.map("Treeview", background=[("selected", "#1f3247")], foreground=[("selected", "#00f0ff")])

        # Top Security Header
        header = tk.Frame(self, bg="#11161f", height=48)
        header.pack(fill="x", side="top")
        self.status_banner = tk.Label(
            header,
            text="  LAYER 05 ZERO-TRUST GUARDRAIL SANDBOX  |  DB: jroc_os_vault.db  |  LIVE AUTO-POLL: 2.0s",
            fg="#00f0ff", bg="#11161f", font=("Consolas", 10, "bold")
        )
        self.status_banner.pack(side="left", pady=12)

        tk.Button(
            header, text="+ INJECT TEST ACTION", command=self._inject_sample,
            bg="#1b2432", fg="#8be9fd", font=("Consolas", 9, "bold"), relief="flat", padx=12, pady=5
        ).pack(side="right", padx=12, pady=8)

        # Filter Strip
        filter_bar = tk.Frame(self, bg="#090c10")
        filter_bar.pack(fill="x", padx=14, pady=(10, 4))
        self.filter_var = tk.StringVar(value="PENDING_APPROVAL")
        for label, val in [("PENDING APPROVAL", "PENDING_APPROVAL"), ("APPROVED", "APPROVED"), ("BLOCKED", "BLOCKED"), ("ALL RECORDS", "ALL")]:
            tk.Radiobutton(
                filter_bar, text=label, variable=self.filter_var, value=val, command=self._refresh_queue,
                bg="#11161f", fg="#00f0ff", selectcolor="#1b2432", indicatoron=0,
                font=("Consolas", 9, "bold"), padx=14, pady=6, relief="flat"
            ).pack(side="left", padx=(0, 8))

        self.counter_label = tk.Label(filter_bar, text="QUEUE: 0", fg="#50fa7b", bg="#090c10", font=("Consolas", 10, "bold"))
        self.counter_label.pack(side="right", padx=6)

        # Main Split Body
        body = tk.Frame(self, bg="#090c10")
        body.pack(fill="both", expand=True, padx=14, pady=8)

        # Left Queue Table
        left_panel = tk.Frame(body, bg="#11161f")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("ID", "SWARM", "ACTION", "STATUS", "TIMESTAMP")
        self.tree = ttk.Treeview(left_panel, columns=cols, show="headings")
        widths = {"ID": 55, "SWARM": 180, "ACTION": 210, "STATUS": 150, "TIMESTAMP": 180}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Right Payload Inspector & Gate Controls
        right_panel = tk.Frame(body, bg="#11161f", width=410)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="SANDBOX PAYLOAD INSPECTOR", fg="#00f0ff", bg="#11161f", font=("Consolas", 11, "bold")).pack(pady=(12, 6))

        self.payload_box = tk.Text(
            right_panel, bg="#07090d", fg="#e6edf3", font=("Consolas", 10),
            relief="flat", padx=10, pady=10, wrap="word"
        )
        self.payload_box.pack(fill="both", expand=True, padx=12, pady=8)
        self.payload_box.insert("end", "Select any queued swarm action on the left to inspect its sandboxed payload before execution.")

        # Action Gate Buttons
        btn_frame = tk.Frame(right_panel, bg="#11161f")
        btn_frame.pack(fill="x", padx=12, pady=(4, 8))

        tk.Button(
            btn_frame, text="APPROVE & EXECUTE", command=lambda: self._decide_selected("APPROVED"),
            bg="#50fa7b", fg="#090c10", font=("Consolas", 10, "bold"), relief="flat", pady=10
        ).pack(fill="x", pady=(0, 6))

        tk.Button(
            btn_frame, text="BLOCK & QUARANTINE", command=lambda: self._decide_selected("BLOCKED"),
            bg="#ff5555", fg="#ffffff", font=("Consolas", 10, "bold"), relief="flat", pady=10
        ).pack(fill="x", pady=(0, 6))

        tk.Button(
            btn_frame, text="APPROVE ALL PENDING", command=self._approve_all_pending,
            bg="#1b2432", fg="#00f0ff", font=("Consolas", 9, "bold"), relief="flat", pady=8
        ).pack(fill="x")

    def _refresh_queue(self):
        current_sel = self.selected_id
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        flt = self.filter_var.get()
        if flt == "ALL":
            cur.execute("SELECT id, swarm_name, action_type, status, created_at FROM guardrail_queue ORDER BY id DESC")
        else:
            cur.execute("SELECT id, swarm_name, action_type, status, created_at FROM guardrail_queue WHERE status=? ORDER BY id DESC", (flt,))
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM guardrail_queue WHERE status='PENDING_APPROVAL'")
        pending_count = cur.fetchone()[0]
        conn.close()

        self.counter_label.config(text=f"PENDING GATE: {pending_count}")
        for r in rows:
            item_id = self.tree.insert("", "end", values=r)
            if current_sel and r[0] == current_sel:
                self.tree.selection_set(item_id)

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.selected_id = int(vals[0])

        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute("SELECT swarm_name, action_type, payload, status, created_at FROM guardrail_queue WHERE id=?", (self.selected_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            self.payload_box.delete("1.0", "end")
            try:
                pretty = json.dumps(json.loads(row[2]), indent=2)
            except Exception:
                pretty = row[2]
            detail = (
                f"RECORD ID : #{self.selected_id}\n"
                f"SWARM     : {row[0]}\n"
                f"ACTION    : {row[1]}\n"
                f"STATUS    : {row[3]}\n"
                f"TIMESTAMP : {row[4]}\n"
                f"{'-'*42}\n"
                f"PAYLOAD:\n{pretty}"
            )
            self.payload_box.insert("end", detail)

    def _decide_selected(self, decision: str):
        if not self.selected_id:
            messagebox.showinfo("Layer 05 Guardrail", "Select an action from the queue first.")
            return
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute("SELECT swarm_name, action_type, payload FROM guardrail_queue WHERE id=?", (self.selected_id,))
        row = cur.fetchone()
        cur.execute("UPDATE guardrail_queue SET status=? WHERE id=?", (decision, self.selected_id))
        conn.commit()
        conn.close()

        if decision == "APPROVED" and row:
            with open(OUTBOUND_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "id": self.selected_id,
                    "swarm": row[0],
                    "action": row[1],
                    "payload": row[2],
                    "approved_at": datetime.utcnow().isoformat()
                }) + "\n")
            speak_status(f"Action {self.selected_id} approved and dispatched.")
        else:
            speak_status(f"Action {self.selected_id} blocked by guardrail.")

        self.selected_id = None
        self._refresh_queue()

    def _approve_all_pending(self):
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute("SELECT id, swarm_name, action_type, payload FROM guardrail_queue WHERE status='PENDING_APPROVAL'")
        rows = cur.fetchall()
        if not rows:
            conn.close()
            return
        cur.execute("UPDATE guardrail_queue SET status='APPROVED' WHERE status='PENDING_APPROVAL'")
        conn.commit()
        conn.close()

        with open(OUTBOUND_LOG, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps({
                    "id": r[0],
                    "swarm": r[1],
                    "action": r[2],
                    "payload": r[3],
                    "approved_at": datetime.utcnow().isoformat()
                }) + "\n")
        speak_status(f"Approved {len(rows)} pending swarm actions.")
        self._refresh_queue()

    def _inject_sample(self):
        conn = sqlite3.connect(str(VAULT_DB))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO guardrail_queue (swarm_name, action_type, payload, status, created_at) VALUES (?, ?, ?, 'PENDING_APPROVAL', ?)",
            ("STUDIO_SWARM", "EXPORT_STORYBOARD_PACK", json.dumps({
                "project": "Reaper Squad - Philadelphia Arc",
                "format": "25-Page Script & Frame Spec",
                "target": "Local Vault + Studio"
            }), datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
        self._refresh_queue()

    def _auto_poll(self):
        self._refresh_queue()
        self.after(2000, self._auto_poll)


if __name__ == "__main__":
    app = GuardrailApprovalDashboard()
    app.mainloop()
"""

def install():
    base = get_base_dir()
    l5_dir = base / "layer-05-security-sandbox"
    l5_dir.mkdir(parents=True, exist_ok=True)
    dash_path = l5_dir / "guardrail_dashboard.py"
    dash_path.write_text(GUARDRAIL_DASHBOARD_CODE, encoding="utf-8")

    if platform.system() == "Windows":
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            bat = desktop / "Jroc_Guardrail_Approval_Dashboard.bat"
            bat.write_text(f'@echo off\nstart "" pythonw "{dash_path}"\n', encoding="utf-8")

    subprocess.Popen([sys.executable, str(dash_path)])

if __name__ == "__main__":
    install()
