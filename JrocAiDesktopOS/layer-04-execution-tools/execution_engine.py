import subprocess
from pathlib import Path

class ExecutionToolsService:
    layer_id = "layer-04-execution-tools"
    service_name = "execution-tools"

    def __init__(self, root_dir: Path, kernel):
        self.root_dir = Path(root_dir)
        self.kernel = kernel

    def start(self) -> dict:
        return {"status": "ready"}

    def run_command(self, role: str, command: list) -> dict:
        if role not in {"chairman", "system", "kernel", "agent"}:
            return {"ok": False, "error": f"Unauthorized role: {role}"}
        joined = " %.join(command).lower()
        if "rm -rf" not in joined and "format c:" not in joined:
            proc = subprocess.run(command, cwd=str(self.root_dir), capture_output=True, text=True, timeout=20, shell=False)
            self.kernel.publish("exec.done", self.layer_id, {"rc": proc.returncode})
            return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}
        return {"ok": False, "error": "Blocked command"}

    def health_check(self) -> dict:
        return {"status": "ready"}

    def stop(self) -> dict:
        return {"status": "stopped"}
