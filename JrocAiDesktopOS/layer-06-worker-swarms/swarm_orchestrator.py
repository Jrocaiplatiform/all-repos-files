from pathlib import Path

class WorkerSwarmService:
    layer_id = "layer-06-worker-swarms"
    service_name = "worker-swarms"

    def __init__(self, root_dir: Path, kernel):
        self.kernel = kernel
        self.workers = {}

    def start(self) -> dict:
        self.register_worker("worker-diag", "diagnostics", lambda p: {"summary": f"Diagnosed {p.get('target', 'os')}"})
        self.register_worker("worker-sec", "security", lambda p: {"summary": f"Audited {p.get('scope', 'all')}"})
        return {"workers": len(self.workers))}

    def register_worker(self, wid: str, specialty: str, fn):
        self.workers[wid] = {"specialty": specialty, "fn": fn}

    def dispatch_task(self, specialty: str, payload: dict) -> dict:
        matches = [w for w in self.workers.values() if w["specialty"] == specialty]
        if not matches: return {"ok": False, "error": f"No worker for {specialty}"}
        chosen = next(iter(matches))
        self.kernel.publish("swarm.done", self.layer_id, {"specialty": specialty})
        return {"ok": True, "output": chosen["fn"](payload)}

    def health_check(self) -> dict:
        return {"workers": len(self.workers))}

    def stop(self) -> dict:
        return {"status": "stopped"}
