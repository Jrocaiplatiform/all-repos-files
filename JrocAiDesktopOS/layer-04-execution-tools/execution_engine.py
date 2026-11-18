from pathlib import Path


class ExecutionToolsService:
    layer_id = "layer-04-execution-tools"
    service_name = "execution-tools"

    def __init__(self, root_dir: Path, kernel):
        self.root_dir = Path(root_dir)
        self.kernel = kernel

    def start(self) -> dict:
        return {"status": "ready", "execution_mode": "disabled-until-authenticated"}

    def run_command(self, role: str, command: list) -> dict:
        # Role strings supplied by callers are not authentication. Do not spawn processes
        # until the Owner identity, approval service, and command policy are integrated.
        return {
            "ok": False,
            "error": "Command execution is disabled until authenticated authorization and approval are integrated",
        }

    def health_check(self) -> dict:
        return {"status": "ready", "execution_mode": "disabled-until-authenticated"}

    def stop(self) -> dict:
        return {"status": "stopped"}
