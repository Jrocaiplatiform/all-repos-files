import hashlib
import hmac
import logging
import os
import platform
import secrets
import time
import uuid
from pathlib import Path

import psutil


class JrocKernel:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = Path(root_dir) if root_dir else Path(__file__).resolve().parent.parent
        data_dir = self.root_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.secret = self._load_secret(data_dir / "kernel.secret")
        self.services = {}
        self.events = []
        self.kernel_token = self.issue_token("layer-01-kernel", "kernel")

    @staticmethod
    def _load_secret(secret_path: Path) -> bytes:
        try:
            fd = os.open(str(secret_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            secret = secret_path.read_bytes().strip()
            if len(secret) < 32:
                raise ValueError(f"Kernel secret is invalid: {secret_path}")
            return secret
        else:
            secret = secrets.token_hex(32).encode("ascii")
            with os.fdopen(fd, "wb") as stream:
                stream.write(secret)
                stream.flush()
                os.fsync(stream.fileno())
            return secret

    def issue_token(self, sid: str, role: str = "system", ttl: int = 86400) -> str:
        if ttl <= 0 or not sid or ":" in sid or not role or ":" in role:
            raise ValueError("A valid service ID, role, and positive TTL are required")
        exp = int(time.time()) + ttl
        payload = f"{sid}:{role}:{exp}"
        sig = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    def verify_token(self, token: str) -> bool:
        try:
            sid, role, exp_s, sig = token.split(":")
            if not sid or not role or int(exp_s) < int(time.time()):
                return False
        except (AttributeError, TypeError, ValueError):
            return False
        expected = hmac.new(
            self.secret, f"{sid}:{role}:{exp_s}".encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(sig, expected)

    def publish(self, topic: str, layer: str, payload: dict):
        self.events.append({
            "id": str(uuid.uuid4()),
            "topic": topic,
            "layer": layer,
            "payload": payload,
        })

    def attach_service(self, svc):
        if not getattr(svc, "service_name", None):
            raise ValueError("Service must define service_name")
        if svc.service_name in self.services:
            raise ValueError(f"Duplicate service: {svc.service_name}")
        self.services[svc.service_name] = svc

    def boot(self) -> dict:
        started = []
        try:
            for name, svc in self.services.items():
                svc.start()
                started.append(name)
        except Exception:
            for name in reversed(started):
                try:
                    self.services[name].stop()
                except Exception:
                    logging.exception("Failed to roll back service %s", name)
            raise

        hardware = {
            "platform": platform.system(),
            "cpu_percent": psutil.cpu_percent(interval=0.05),
            "memory_percent": psutil.virtual_memory().percent,
        }
        self.publish("kernel.booted", "layer-01", hardware)
        return {
            "status": "online",
            "layers_active": len(started) + 1,
            "services": started,
            "hardware": hardware,
        }

    def health(self) -> dict:
        return {
            "kernel": "online",
            "services": {name: svc.health_check() for name, svc in self.services.items()},
        }

    def shutdown(self) -> dict:
        errors = []
        for name, svc in reversed(list(self.services.items())):
            try:
                svc.stop()
            except Exception as exc:
                errors.append({"service": name, "error": str(exc)})
        return {"status": "offline" if not errors else "degraded", "errors": errors}
