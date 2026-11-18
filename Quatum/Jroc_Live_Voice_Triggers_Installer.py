import os
import sys
import json
import subprocess
from pathlib import Path

if os.name == "nt":
    BASE_DIR = Path(r"C:\J-roc-AI\JrocAiDesktopOS")
else:
    BASE_DIR = Path.home() / "JrocAiDesktopOS"

L07_DIR = BASE_DIR / "layer-07-jbot-core"
L09_DIR = BASE_DIR / "layer-09-industrial-hud"

for d in [L07_DIR, L09_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 1. Layer 07: Live Hands-Free Voice Trigger & Speech Engine
voice_triggers_py = """import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "layer-06-worker-swarms"))
sys.path.insert(0, str(BASE_DIR / "layer-07-jbot-core"))

try:
    from quantum_swarm_engine import QuantumSwarmEngine
except ImportError:
    QuantumSwarmEngine = None

TRIGGER_MAP_PATH = BASE_DIR / "layer-07-jbot-core" / "voice_trigger_map.json"

DEFAULT_TRIGGERS = {
    "wake_words": ["hey j-bot", "hey jbot", "j-bot", "jbot", "j-roc"],
    "division_triggers": {
        "DEV_OPS": ["build app", "dev swarm", "deploy factory", "check repo", "code update"],
        "REPAIR_PRO": ["scan device", "repair pro", "check phone", "diagnostics", "frp fix"],
        "COMMERCE": ["appraise", "check comps", "price item", "sports card", "store listing"],
        "STUDIO": ["studio", "make beat", "comic script", "storyboard", "reaper squad"]
    },
    "system_commands": {
        "RUN_ANNEALING": ["optimize queue", "quantum sort", "run annealing", "prioritize tasks"],
        "BENCHMARK_MODELS": ["benchmark models", "rank models", "test free models"],
        "STOP_LISTENING": ["sleep j-bot", "pause voice", "mute mic"]
    }
}

class JBotHandsFreeVoiceController:
    def __init__(self, on_status_callback=None, on_transcript_callback=None, on_result_callback=None):
        self.on_status = on_status_callback or (lambda msg: None)
        self.on_transcript = on_transcript_callback or (lambda text: None)
        self.on_result = on_result_callback or (lambda res: None)
        self.listening = False
        self._thread = None
        self.engine = QuantumSwarmEngine() if QuantumSwarmEngine else None

        if not TRIGGER_MAP_PATH.exists():
            TRIGGER_MAP_PATH.write_text(json.dumps(DEFAULT_TRIGGERS, indent=2), encoding="utf-8")
        self.triggers = json.loads(TRIGGER_MAP_PATH.read_text(encoding="utf-8"))

    def speak(self, message: str):
        clean_msg = message.replace('"', "").replace("'", "").replace("\n", " ")[:240]
        if os.name == "nt":
            ps_cmd = (
                f'Add-Type -AssemblyName System.Speech; '
                f'$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                f'$s.Rate = 1; '
                f'$s.Speak("{clean_msg}");'
            )
            subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def match_intent(self, spoken_text: str) -> dict:
        lower = spoken_text.lower().strip()
        wake_detected = False
        cleaned = lower

        for wake in self.triggers.get("wake_words", []):
            if wake in lower:
                wake_detected = True
                cleaned = lower.replace(wake, "", 1).strip(" ,.!?")
                break

        for sys_action, phrases in self.triggers.get("system_commands", {}).items():
            for p in phrases:
                if p in lower:
                    return {"wake": True, "type": "SYSTEM", "action": sys_action, "command": cleaned or lower}

        for div, phrases in self.triggers.get("division_triggers", {}).items():
            for p in phrases:
                if p in lower:
                    return {"wake": True, "type": "SWARM", "division": div, "command": cleaned or lower}

        if wake_detected and cleaned:
            return {"wake": True, "type": "SWARM", "division": "DEV_OPS", "command": cleaned}

        return {"wake": False, "type": "IGNORED", "command": lower}

    def process_spoken_phrase(self, phrase: str):
        self.on_transcript(phrase)
        intent = self.match_intent(phrase)
        if not intent["wake"]:
            return

        if intent["type"] == "SYSTEM":
            act = intent["action"]
            if act == "STOP_LISTENING":
                self.stop()
                self.speak("J-Bot voice trigger paused.")
                return
            elif act == "RUN_ANNEALING" and self.engine:
                self.on_status("EXECUTING QUANTUM ANNEALING...")
                self.speak("Running quantum annealing queue optimization.")
                sample = [
                    {"task": "Diagnostics Queue", "urgency": 9, "effort": 2},
                    {"task": "Store Appraisal Batch", "urgency": 8, "effort": 3},
                    {"task": "Factory App Build", "urgency": 7, "effort": 4}
                ]
                ranked = self.engine.annealing_solver.optimize_task_queue(sample)
                self.on_result({"type": "ANNEALING", "data": ranked})
                return
            elif act == "BENCHMARK_MODELS":
                self.on_status("BENCHMARKING FREE MODELS...")
                self.speak("Starting Layer 11 model speed benchmark.")
                self.on_result({"type": "SYSTEM", "data": "Layer 11 Auto-Benchmarker triggered."})
                return

        if intent["type"] == "SWARM":
            div = intent["division"]
            cmd = intent["command"]
            self.on_status(f"QUANTUM SWARM DISPATCH -> {div}")
            self.speak(f"Routing to {div.replace('_', ' ')} swarm.")
            if self.engine:
                res = self.engine.dispatch_quantum_workflow(div, cmd)
                self.on_result({"type": "SWARM", "division": div, "data": res})
                self.speak(f"Complete. Winning branch {res.get('winning_branch')} finished in {res.get('latency_ms')} milliseconds.")
            else:
                self.on_result({"type": "SWARM", "division": div, "data": {"output": f"Simulated dispatch: {cmd}"}})

    def start(self):
        if self.listening:
            return
        self.listening = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.listening = False
        self.on_status("VOICE HUD: STANDBY (MUTED)")

    def _listen_loop(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True
            mic = sr.Microphone()
            with mic as source:
                self.on_status("CALIBRATING AMBIENT MIC...")
                recognizer.adjust_for_ambient_noise(source, duration=0.8)
            self.on_status("LIVE HANDS-FREE LISTENING (SAY 'HEY J-BOT')")
            self.speak("J-Bot live voice triggers online.")

            while self.listening:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=10)
                    text = recognizer.recognize_google(audio)
                    if text:
                        self.process_spoken_phrase(text)
                except Exception:
                    continue
        except ImportError:
            self.on_status("MIC LIB MISSING -> VOICE TRIGGER SIMULATOR READY")
            self.speak("Voice trigger controller loaded in simulation mode.")
"""

(L07_DIR / "live_voice_triggers.py").write_text(voice_triggers_py, encoding="utf-8")

# 2. Layer 09: Live Hands-Free Voice HUD & Quantum Trigger Console
voice_hud_app_py = """import tkinter as tk
import sys
import json
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "layer-07-jbot-core"))
from live_voice_triggers import JBotHandsFreeVoiceController, DEFAULT_TRIGGERS

class JBotLiveVoiceHUD(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JROC AI DESKTOP OS // LAYER 07 LIVE HANDS-FREE VOICE TRIGGER HUD")
        self.geometry("1150x740")
        self.configure(bg="#070a0f")

        self.pulse_phase = 0.0
        self.is_live = False

        self.controller = JBotHandsFreeVoiceController(
            on_status_callback=self._update_status,
            on_transcript_callback=self._on_transcript,
            on_result_callback=self._on_result
        )
        self._build_ui()
        self._animate_orb()
        self.after(400, self._toggle_mic)

    def _build_ui(self):
        # Top Status Strip
        top = tk.Frame(self, bg="#0f1622", height=44)
        top.pack(fill="x", side="top")
        self.status_var = tk.StringVar(value="INITIALIZING HANDS-FREE VOICE ENGINE...")
        tk.Label(
            top, textvariable=self.status_var, fg="#00f0ff", bg="#0f1622",
            font=("Consolas", 10, "bold")
        ).pack(side="left", padx=14, pady=10)

        self.mic_btn = tk.Button(
            top, text="MUTE MIC", command=self._toggle_mic,
            bg="#ff4d6d", fg="#ffffff", font=("Consolas", 9, "bold"), relief="flat", padx=12, pady=4
        )
        self.mic_btn.pack(side="right", padx=14, pady=8)

        # Center Split
        body = tk.Frame(self, bg="#070a0f")
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # Left Panel: Voice Orb & Quick Trigger Simulator
        left = tk.Frame(body, bg="#0f1622", width=360)
        left.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(left, text="J-BOT VOICE ORB", fg="#ffffff", bg="#0f1622", font=("Consolas", 11, "bold")).pack(pady=(12, 4))
        self.orb_canvas = tk.Canvas(left, width=220, height=220, bg="#0f1622", highlightthickness=0)
        self.orb_canvas.pack(pady=6)

        tk.Label(left, text="HANDS-FREE TRIGGER PHRASES", fg="#00f0ff", bg="#0f1622", font=("Consolas", 10, "bold")).pack(pady=(8, 4))
        triggers_info = (
            "Wake Words: 'Hey J-Bot', 'J-Bot', 'J-Roc'\n\n"
            "• 'Hey J-Bot, scan device' -> REPAIR_PRO\n"
            "• 'Hey J-Bot, appraise card' -> COMMERCE\n"
            "• 'Hey J-Bot, build app' -> DEV_OPS\n"
            "• 'Hey J-Bot, reaper squad script' -> STUDIO\n"
            "• 'Hey J-Bot, optimize queue' -> ANNEALING\n"
            "• 'Hey J-Bot, mute mic' -> PAUSE VOICE"
        )
        tk.Label(left, text=triggers_info, fg="#94a3b8", bg="#0a0e17", justify="left", font=("Consolas", 9), padx=10, pady=10).pack(fill="x", padx=12)

        tk.Label(left, text="INSTANT TRIGGER TEST (NO MIC NEEDED)", fg="#50fa7b", bg="#0f1622", font=("Consolas", 9, "bold")).pack(pady=(12, 4))
        quick_cmds = [
            "Hey J-Bot, scan device for display and NFC errors",
            "Hey J-Bot, appraise vintage 1996 Kobe rookie card",
            "Hey J-Bot, build app module for AI Factory",
            "Hey J-Bot, optimize queue with quantum annealing"
        ]
        for q in quick_cmds:
            tk.Button(
                left, text=q[:38] + "...", command=lambda cmd=q: self.controller.process_spoken_phrase(cmd),
                bg="#182234", fg="#e2e8f0", anchor="w", font=("Consolas", 8), relief="flat", padx=8, pady=5
            ).pack(fill="x", padx=12, pady=2)

        # Right Panel: Live Transcript & Quantum Swarm Output
        right = tk.Frame(body, bg="#0f1622")
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="LIVE VOICE TRANSCRIPT & QUANTUM SWARM FEED", fg="#00f0ff", bg="#0f1622", font=("Consolas", 11, "bold")).pack(pady=10)
        self.feed = tk.Text(right, bg="#05070b", fg="#e6edf3", font=("Consolas", 10), relief="flat", padx=12, pady=12)
        self.feed.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.feed.insert("end", "[LAYER 07] Hands-Free Voice Trigger HUD ready. Speak a wake phrase or click a test trigger on the left.\n\n")

    def _animate_orb(self):
        self.orb_canvas.delete("all")
        cx, cy = 110, 110
        self.pulse_phase += 0.12
        pulse = math.sin(self.pulse_phase) * (10 if self.is_live else 2)
        r_outer = 78 + pulse
        r_inner = 48 - (pulse * 0.5)

        outer_color = "#00f0ff" if self.is_live else "#334155"
        inner_color = "#0284c7" if self.is_live else "#1e293b"

        self.orb_canvas.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, outline=outer_color, width=3)
        self.orb_canvas.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, fill=inner_color, outline="#38bdf8", width=2)
        label = "LISTENING" if self.is_live else "MUTED"
        self.orb_canvas.create_text(cx, cy, text=label, fill="#ffffff", font=("Consolas", 10, "bold"))
        self.after(50, self._animate_orb)

    def _toggle_mic(self):
        if not self.is_live:
            self.is_live = True
            self.mic_btn.config(text="MUTE MIC", bg="#ff4d6d")
            self.controller.start()
        else:
            self.is_live = False
            self.mic_btn.config(text="ENABLE HANDS-FREE MIC", bg="#50fa7b", fg="#05070b")
            self.controller.stop()

    def _update_status(self, msg: str):
        self.after(0, lambda: self.status_var.set(msg))

    def _on_transcript(self, text: str):
        def _append():
            self.feed.insert("end", f"[VOICE HEARD] \"{text}\"\n")
            self.feed.see("end")
        self.after(0, _append)

    def _on_result(self, payload: dict):
        def _append():
            ptype = payload.get("type")
            if ptype == "SWARM":
                div = payload.get("division")
                res = payload.get("data", {})
                self.feed.insert("end", f"[QUANTUM DISPATCH -> {div}] Branch: {res.get('winning_branch', 'local')} | Latency: {res.get('latency_ms', 0)}ms\n")
                self.feed.insert("end", f"{res.get('output', '')}\n\n")
            else:
                self.feed.insert("end", f"[{ptype}] {json.dumps(payload.get('data'), indent=2)}\n\n")
            self.feed.see("end")
        self.after(0, _append)

if __name__ == "__main__":
    app = JBotLiveVoiceHUD()
    app.mainloop()
"""

(L09_DIR / "jbot_live_voice_hud.py").write_text(voice_hud_app_py, encoding="utf-8")

# 3. Desktop Shortcut
if os.name == "nt":
    desktop = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    bat_path = desktop / "Jbot_Live_Voice_Triggers.bat"
    bat_path.write_text(
        f'@echo off\nstart "" pythonw "{L09_DIR / "jbot_live_voice_hud.py"}"\n',
        encoding="utf-8"
    )

print("Installed Layer 07 Live Hands-Free Voice Triggers & Layer 09 Voice HUD.")
subprocess.Popen([sys.executable, str(L09_DIR / "jbot_live_voice_hud.py")])
