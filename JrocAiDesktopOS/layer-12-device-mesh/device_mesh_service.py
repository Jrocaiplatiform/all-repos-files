import hashlib
import hmac
import time
from pathlib import Path


class DeviceMeshService:
    layer_id = "layer-12-device-mesh"
    service_name = "device-mesh"

    def __init__(self, root_dir: Path, secret: bytes, kernel):
        self._secret = secret
        self.kernel = kernel
        self.nodes = {}

    def start(self) -> dict:
        self.register_node("local-workstation", "Windows")
        return {"nodes": len(self.nodes)}

    def register_node(self, node_id: str, platform_name: str) -> str:
        if not node_id or not platform_name:
            raise ValueError("Node ID and platform are required")
        self.nodes[node_id] = platform_name
        expires_at = int(time.time()) + 86400
        payload = f"{node_id}:{platform_name}:{expires_at}"
        signature = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        self.kernel.publish("mesh.node", self.layer_id, {"node": node_id})
        return f"{payload}:{signature}"

    def health_check(self) -> dict:
        return {"nodes": dict(self.nodes)}

    def stop(self) -> dict:
        return {"status": "stopped"}
