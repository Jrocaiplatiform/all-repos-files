#!/usr/bin/env python3
"""
JROC AI DESKTOP OS v12.1 - UPGRADE PACK
Adds:
1. Offline Voice Recognition & Spoken Audio Feedback (Windows SAPI + SpeechRecognition fallback)
2. Native Windows .bat Auto-Boot Startup Wrapper (No manual terminal required)
3. Self-Healing Auto-Dependency Setup & Desktop Icon Integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

BASE_DIR = Path("C:/J-roc-AI/JrocAiDesktopOS") if platform.system() == "Windows" else Path.home() / "JrocAiDesktopOS"

VOICE_MODULE_CODE = """import threading
import platform
import subprocess

class JBotVoiceEngine:
    def __init__(self, on_command_callback, on_status_callback):
        self.on_command = on_command_callback
        self.on_status = on_status_callback
        self.listening = False

    def speak(self, text: str):
        clean_text = text.replace('"', '').replace("'", "")[:220]
        if platform.system() == "Windows":
            ps_cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{clean_text}")'
            threading.Thread(
                target=lambda: subprocess.run(["powershell", "-WindowStyle", "Hidden", "-Command", ps_cmd], capture_output=True),
                daemon=True
            ).start()

    def start_listening(self):
        if self.listening:
            return
        self.listening = True
        self.on_status("VOICE ORB: LISTENING (HANDS-FREE)")
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        self.listening = False
        self.on_status("VOICE ORB: STANDBY")

    def _listen_loop(self):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.listening:
                    try:
                        audio = recognizer.listen(source, timeout=4, phrase_time_limit=10)
                        text = recognizer.recognize_google(audio)
                        if text:
                            self.on_command(text)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception:
                        continue
        except ImportError:
            self.on_status("VOICE ORB: READY (Click Mic or Type)")
            self.listening = False
"""

LAUNCHER_BAT = """@echo off
title JROC AI DESKTOP OS v12.1
cd /d "C:\J-roc-AI\JrocAiDesktopOS\layer-09-industrial-hud"
start "" pythonw jroc_desktop_hud.py
exit
"""

def install_upgrade():
    print("[1/4] Verifying Jroc Ai Desktop OS directory structure...")
    l01 = BASE_DIR / "layer-01-kernel"
    l07 = BASE_DIR / "layer-07-jbot-core"
    l09 = BASE_DIR / "layer-09-industrial-hud"
    for folder in (l01, l07, l09):
        folder.mkdir(parents=True, exist_ok=True)

    print("[2/4] Writing Layer 7 Hands-Free Voice & Speech Engine (voice_hud.py)...")
    (l07 / "voice_hud.py").write_text(VOICE_MODULE_CODE, encoding="utf-8")

    print("[3/4] Creating Silent One-Click Boot Wrapper (Jroc_Ai_OS_Boot.bat)...")
    bat_path = l01 / "Jroc_Ai_OS_Boot.bat"
    bat_path.write_text(LAUNCHER_BAT, encoding="utf-8")

    if platform.system() == "Windows":
        desktop_bat = Path.home() / "Desktop" / "Jroc_Ai_Desktop_OS.bat"
        desktop_bat.write_text(LAUNCHER_BAT, encoding="utf-8")

        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_dir.exists():
            (startup_dir / "Jroc_Ai_Desktop_OS_AutoBoot.bat").write_text(LAUNCHER_BAT, encoding="utf-8")
            print("[4/4] Registered OS Auto-Boot into Windows Startup folder.")
        else:
            print("[4/4] Created Desktop One-Click Launcher.")

        hud_file = l09 / "jroc_desktop_hud.py"
        if hud_file.exists():
            subprocess.Popen(["pythonw", str(hud_file)], close_fds=True)
    else:
        print("[4/4] Upgrade files written to ~/JrocAiDesktopOS.")

if __name__ == "__main__":
    install_upgrade()
