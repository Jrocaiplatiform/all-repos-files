from pathlib import Path


class WorkerSwarmService:
    layer_id = "layer-06-worker-swarms"
    service_name = "worker-swarms"

    def __init__(self, root_dir: Path, kernel):
        self.kernel = kernel
        self.workers = {}

    def start(self) -> dict:
        self.register_worker(
            "worker-diag",
            "diagnostics",
            lambda payload: {"summary": f"Diagnosed {payload.get('target', 'os')}"},
        )
        self.register_worker(
            "worker-sec",
            "security",
            lambda payload: {"summary": f"Audited {payload.get('scope', 'all')}"},
        )
        return {"workers": len(self.workers)}

    def register_worker(self, worker_id: str, specialty: str, fn):
        if not worker_id or not specialty or not callable(fn):
            raise ValueError("Worker ID, specialty, and callable handler are required")
        self.workers[worker_id] = {"specialty": specialty, "fn": fn}

    def dispatch_task(self, specialty: str, payload: dict) -> dict:
        matches = [worker for worker in self.workers.values() if worker["specialty"] == specialty]
        if not matches:
            return {"ok": False, "error": f"No worker for {specialty}"}
        worker = matches[0]
        output = worker["fn"](payload)
        self.kernel.publish("swarm.done", self.layer_id, {"specialty": specialty})
        return {"ok": True, "output": output}

    def health_check(self) -> dict:
        return {"workers": len(self.workers)}

    def stop(self) -> dict:
        return {"status": "stopped"}
