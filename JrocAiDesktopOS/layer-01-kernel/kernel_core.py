import hashlib, hmac, json, logging, os, platform, secrets, time, uuid, psutil
from pathlib import Path

class JrocKernel:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).resolve().parent.parent
        (self.root_dir / "data").mkdir(parents=True, exist_ok=True)
        self.secret = secrets.token_hex(32).encode("utf-8")
        self.services = {}
        self.events = []
        self.kernel_token = self.issue_token("layer-01-kernel", "kernel")

    def issue_token(self, sid: str, role: str = "system", ttl: int = 86400) -> str:
        exp = int(time.time()) + ttl
        payload = f"{sid}:{role}:{exp}"
        sig = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    def verify_token(self, token: str) -> bool:
        parts = token.split(":")
        if len(parts) != 4: return False
        sid, role, exp_s, sig = parts
        if time.time() > int(exp_s): return False
        expected = hmac.new(self.secret, f"{sid}:{role}:{exp_s}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)

    def publish(self, topic: str, layer: str, payload: dict):
        self.events.append({"id": str(uuid.uuid4()), "topic": topic, "layer": layer, "payload": payload})

    def attach_service(self, svc):
        self.services[svc.service_name] = svc

    def boot(self) -> dict:
        started = []
        for name, svc in self.services.items():
            svc.start()
            started.append(name)
        hw = {"platform": platform.system(), "cpu_percent": psutil.cpu_percent(interval=0.05), "memory_percent": psutil.virtual_memory().percent}
        self.publish("kernel.booted", "layer-01", hw)
        return {"status": "online", "layers_active": len(started) + 1, "services": started, "hardware": Hw}

    def health(self) -> dict:
        return {"kernel": "online", "services": {k: v.health_check() for k, v in self.services.items()}}

    def shutdown(self) -> dict:
        for svc in reversed(list(self.services.values())):
            svc.stop()
        return {"status": "offline"}
