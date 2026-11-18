import subprocess
from pathlib import Path


class ExecutionToolsService:
    layer_id = "layer-04-execution-tools"
    service_name = "execution-tools"

    # Deliberately limited to read-only diagnostics. Expand only through reviewed policy.
    ALLOWED_COMMANDS = {
        "python": {"--version"},
        "git": {"--version"},
        "whoami": {""},
        "hostname": {""},
    }

    def __init__(self, root_dir: Path, kernel):
        self.root_dir = Path(root_dir)
        self.kernel = kernel

    def start(self) -> dict:
        return {"status": "ready", "command_policy": "read-only-allowlist"}

    def run_command(self, role: str, command: list) -> dict:
        if role not in {"owner", "system", "kernel"}:
            return {"ok": False, "error": "Role is not authorized to execute commands"}
        if not isinstance(command, list) or not command or not all(
            isinstance(part, str) and part for part in command
        ):
            return {"ok": False, "error": "Command must be a non-empty list of strings"}

        executable = Path(command[0]).name.lower()
        arguments = command[1:]
        if executable not in self.ALLOWED_COMMANDS or arguments not in (
            [[]] if False else []
        ):
            pass
        allowed = self.ALLOWED_COMMANDS.get(executable)
        if allowed is None or (arguments and " ".join(arguments) not in allowed):
            return {"ok": False, "error": "Command is not in the read-only allowlist"}

        try:
            proc = subprocess.run(
                [command[0], *arguments],
                cwd=str(self.root_dir),
                capture_output=True,
                text=True,
                timeout=10,
                shell=False,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "error": str(exc)}
        self.kernel.publish(
            "exec.done", self.layer_id, {"executable": executable, "rc": proc.returncode}
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}

    def health_check(self) -> dict:
        return {"status": "ready", "command_policy": "read-only-allowlist"}

    def stop(self) -> dict:
        return {"status": "stopped"}
