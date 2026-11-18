import hashlib, hmac, time
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
        self.nodes[node_id] = platform_name
        exp = int(time.time()) + 86400
        payload = f"{node_id}:{platform_name}:{exp}"
        sig = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        self.kernel.publish("mesh.node", self.layer_id, {"node": node_id})
        return f"{payload}:{sig}"

    def health_check(self) -> dict:
        return {"nodes": self.nodes}

     def stop(self) -> dict:
        return {"status": "stopped"}
