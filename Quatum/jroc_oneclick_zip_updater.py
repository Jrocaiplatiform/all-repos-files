import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import zipfile
import shutil
import threading
from pathlib import Path

BASE_DIR = Path(r"C:\J-roc-AI\JrocAiDesktopOS") if os.name == "nt" else Path.home() / "JrocAiDesktopOS"
TEMP_DIR = BASE_DIR / "_update_temp"
PROTECTED_FILES = {"jroc_os_vault.db", "jroc_telemetry.db", ".env", "custom_swarms.json", "voice_trigger_map.json"}

class JrocOneClickZipUpdater(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JROC AI OS // ONE-CLICK GITHUB RELEASE .ZIP UPDATER")
        self.geometry("780x520")
        self.configure(bg="#0a0d12")
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg="#11161f", height=44)
        top.pack(fill="x")
        tk.Label(
            top,
            text="  JROC AI DESKTOP OS  |  ONE-CLICK GITHUB .ZIP RELEASE UPDATER",
            fg="#00f0ff", bg="#11161f", font=("Consolas", 11, "bold")
        ).pack(side="left", pady=10)

        form = tk.Frame(self, bg="#11161f")
        form.pack(fill="x", padx=14, pady=12)

        tk.Label(form, text="GitHub Owner/Repo:", fg="#8be9fd", bg="#11161f", font=("Consolas", 10, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.repo_slug = tk.Entry(form, bg="#161d29", fg="#ffffff", font=("Consolas", 10), width=42, relief="flat")
        self.repo_slug.insert(0, "Jrocai1/JrocAiDesktopOS")
        self.repo_slug.grid(row=0, column=1, sticky="w", padx=10, pady=8)

        tk.Label(form, text="Target Install Path:", fg="#8be9fd", bg="#11161f", font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.install_dir = tk.Entry(form, bg="#161d29", fg="#ffffff", font=("Consolas", 10), width=42, relief="flat")
        self.install_dir.insert(0, str(BASE_DIR))
        self.install_dir.grid(row=1, column=1, sticky="w", padx=10, pady=8)

        btn_bar = tk.Frame(self, bg="#0a0d12")
        btn_bar.pack(fill="x", padx=14, pady=(0, 8))

        self.update_btn = tk.Button(
            btn_bar, text="PULL LATEST RELEASE .ZIP & APPLY SAFE UPDATE",
            command=self._start_update_thread,
            bg="#00f0ff", fg="#0a0d12", font=("Consolas", 10, "bold"), relief="flat", padx=18, pady=8
        )
        self.update_btn.pack(side="left")

        self.log_box = tk.Text(self, bg="#07090d", fg="#e6edf3", font=("Consolas", 10), relief="flat", padx=12, pady=12)
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._log("[READY] Protected Vault & Configs: jroc_os_vault.db, .env, custom_swarms.json, voice_trigger_map.json")
        self._log("[INFO] Click 'PULL LATEST RELEASE .ZIP & APPLY SAFE UPDATE' to fetch and install your newest GitHub Release.")

    def _log(self, msg: str):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.update_idletasks()

    def _start_update_thread(self):
        self.update_btn.config(state="disabled")
        threading.Thread(target=self._run_update, daemon=True).start()

    def _run_update(self):
        slug = self.repo_slug.get().strip().replace("https://github.com/", "").replace(".git", "").strip("/")
        target = Path(self.install_dir.get().strip())
        target.mkdir(parents=True, exist_ok=True)
        api_url = f"https://api.github.com/repos/{slug}/releases/latest"

        try:
            self._log(f"\n[1/4] Checking latest release metadata from {api_url}...")
            req = urllib.request.Request(api_url, headers={"User-Agent": "JrocAiDesktopOS-Updater"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                release_data = json.loads(resp.read().decode("utf-8"))

            tag = release_data.get("tag_name", "latest")
            assets = release_data.get("assets", [])
            zip_url = None
            zip_name = f"JrocAiDesktopOS-{tag}.zip"

            for asset in assets:
                if asset.get("name", "").endswith(".zip"):
                    zip_url = asset.get("browser_download_url")
                    zip_name = asset.get("name")
                    break

            if not zip_url:
                zip_url = release_data.get("zipball_url")

            if not zip_url:
                raise RuntimeError("No downloadable .zip asset or source archive found in the latest release.")

            if TEMP_DIR.exists():
                shutil.rmtree(TEMP_DIR, ignore_errors=True)
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            zip_path = TEMP_DIR / zip_name

            self._log(f"[2/4] Downloading {zip_name} ({tag})...")
            dl_req = urllib.request.Request(zip_url, headers={"User-Agent": "JrocAiDesktopOS-Updater"})
            with urllib.request.urlopen(dl_req, timeout=60) as dl_resp, open(zip_path, "wb") as out_file:
                shutil.copyfileobj(dl_resp, out_file)

            extract_dir = TEMP_DIR / "extracted"
            self._log("[3/4] Extracting archive and verifying layer structure...")
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            # Handle GitHub zipball single root folder wrapper if present
            entries = list(extract_dir.iterdir())
            source_root = entries[0] if (len(entries) == 1 and entries[0].is_dir() and not (extract_dir / "layer-01-kernel").exists()) else extract_dir

            updated_count = 0
            skipped_count = 0
            for item in source_root.rglob("*"):
                if item.is_dir():
                    continue
                rel = item.relative_to(source_root)
                dest = target / rel
                if item.name in PROTECTED_FILES and dest.exists():
                    skipped_count += 1
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                updated_count += 1

            shutil.rmtree(TEMP_DIR, ignore_errors=True)
            self._log(f"[4/4] Update complete! Updated {updated_count} OS files (preserved {skipped_count} local vault/config files).")
            self._log(f"[SUCCESS] Jroc Ai Desktop OS is now running release {tag}.")
        except Exception as exc:
            self._log(f"[ERROR] Update failed: {exc}")
            self._log("[TIP] Ensure your GitHub repository has at least one published Release from release_packager.yml.")
        finally:
            self.update_btn.config(state="normal")

if __name__ == "__main__":
    import os
    app = JrocOneClickZipUpdater()
    app.mainloop()
