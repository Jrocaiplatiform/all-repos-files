import tkinter as tk
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "layer-07-jbot-core"))
from jroc_core_engine import JrocDesktopOSEngine
from voice_hud import JBotVoiceBridge

class JrocDesktopHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.engine = JrocDesktopOSEngine()
        self.voice = JBotVoiceBridge()
        self.title("JROC AI DESKTOP OS // 12-LAYER INDUSTRIAL COMMAND CENTER")
        self.geometry("1280x800")
        self.configure(bg="#0a0d12")
        self.active_division = tk.StringVar(value="DEV_OPS")
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg="#11161f", height=42)
        top.pack(fill="x", side="top")
        tk.Label(top, text="  JROC AI OS v12.0  |  INFERENCE: LOCAL OLLAMA  |  VAULT: SQLITE  |  INPUT: KEYBOARD", fg="#00f0ff", bg="#11161f", font=("Consolas", 10, "bold")).pack(side="left", pady=10)

        main = tk.Frame(self, bg="#0a0d12")
        main.pack(fill="both", expand=True, padx=12, pady=10)

        left = tk.Frame(main, bg="#11161f", width=300)
        left.pack(side="left", fill="y", padx=(0, 10))
        tk.Label(left, text="12-LAYER SYSTEM MATRIX", fg="#ffffff", bg="#11161f", font=("Consolas", 11, "bold")).pack(pady=10)

        layers = [
            "L12: Device Registry [LOCAL PROTOTYPE]",
            "L11: Upgrade Records [PROTOTYPE]",
            "L10: Revenue & Store Sync [LICENSE STUB]",
            "L09: Industrial HUD Shell [UI LOADED]",
            "L08: Division Workspaces [3 SAMPLE WORKSPACES]",
            "L07: J-Bot Intent Core [TEXT INPUT]",
            "L06: Worker Handlers (2x) [PROTOTYPE]",
            "L05: Security Sandbox [POLICY PROTOTYPE]",
            "L04: Execution Tools [RESTRICTED]",
            "L03: SQLite Memory Vault [LOCAL DATABASE]",
            "L02: Model Router [LOCAL OLLAMA ONLY]",
            "L01: Host Kernel [HARDWARE DETECTED AT RUNTIME]"
        ]
        for l in layers:
            tk.Label(left, text=f"  {l}", fg="#8be9fd", bg="#161d29", anchor="w", font=("Consolas", 9)).pack(fill="x", padx=8, pady=3)

        center = tk.Frame(main, bg="#11161f")
        center.pack(side="left", fill="both", expand=True)
        tk.Label(center, text="J-BOT MASTER ORCHESTRATOR & SWARM FEED", fg="#00f0ff", bg="#11161f", font=("Consolas", 12, "bold")).pack(pady=10)

        self.log = tk.Text(center, bg="#07090d", fg="#e6edf3", font=("Consolas", 10), insertbackground="#00f0ff", relief="flat", padx=12, pady=12)
        self.log.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.log.insert("end", "[SYSTEM] 12-layer prototype loaded. Runtime checks determine service readiness. Enter a text command below.

")

        bar = tk.Frame(center, bg="#11161f")
        bar.pack(fill="x", padx=12, pady=(0, 12))
        self.entry = tk.Entry(bar, bg="#161d29", fg="#ffffff", font=("Consolas", 11), insertbackground="#00f0ff", relief="flat")
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._send())
        tk.Button(bar, text="AUTO-ROUTE & DISPATCH", command=self._send, bg="#00f0ff", fg="#0a0d12", font=("Consolas", 10, "bold"), relief="flat", padx=16, pady=6).pack(side="right")

        dock = tk.Frame(self, bg="#11161f", height=54)
        dock.pack(fill="x", side="bottom")
        for label, code in [("J-ROC AI FACTORY (DEV)", "DEV_OPS"), ("UNIVERSAL REPAIR PRO", "REPAIR_PRO"), ("SPORTS APPRAISER & STORE", "COMMERCE"), ("ENTERTAINMENT STUDIO", "STUDIO")]:
            tk.Button(dock, text=label, command=lambda c=code, l=label: self._switch(c, l), bg="#1b2432", fg="#00f0ff", font=("Consolas", 10, "bold"), relief="flat", padx=14, pady=8).pack(side="left", padx=10, pady=8)

    def _switch(self, code, label):
        self.active_division.set(code)
        self.log.insert("end", f"[DOCK] Active Swarm -> {label}
")
        self.log.see("end")

    def _send(self):
        cmd = self.entry.get().strip()
        if not cmd:
            return
        self.entry.delete(0, "end")
        div = self.voice.parse_voice_intent(cmd)
        self.active_division.set(div)
        self.log.insert("end", f"[J-ROC -> {div}] {cmd}
")
        res = self.engine.dispatch_to_swarm(div, cmd)
        self.log.insert("end", f"[J-BOT | {res['model']} | {res['latency_ms']}ms]
{res['output']}

")
        self.log.see("end")

if __name__ == "__main__":
    JrocDesktopHUD().mainloop()
