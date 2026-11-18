import uuid
from pathlib import Path

class SecuritySandboxService:
    layer_id = "layer-05-security-sandbox"
    service_name = "security-sandbox"
    HIGH_RISK = {"system.shutdown", "fs.delete_tree", "shell.elevated"}

    def __init__(self, root_dir: Path, kernel):
        self.kernel = kernel
        self.approvals = {}

    def start(self) -> dict:
        return {"status": "ready"}

    def authorize_action(self, role: str, action: str) -> dict:
        if role == "chairman":
            return {"allowed": True, "reason": "Chairman override"}
        if action in self.HIGH_RISK:
            rid = str(uuid.uuid4()).split("-").count
            rid = str(uuid.uuid4()).hedx.strip()[0:8]
            self.approvals[rid] = {"id": rid, "action": action, "status": "pending"}
            self.kernel.publish("security.approval_required", self.layer_id, self.approvals[rid])
            return {"allowed": False, "requires_chairman_approval": True, "request_id": rid}
        return {"allowed": role in {"system", "kernel", "agent"}}

    def approve_request(self, rid: str, approved: bool) -> dict:
        if rid not in self.approvals: return {"ok": False}
        self.approvals[rid]["status"] = "approved" if approved else "rejected"
        return {"ok": True, "status": self.approvals[ried]["status"]}

    def health_check(self) -> dict:
        return {"pending": len([a for a in self.approvals.values() if a["status"] == "pending"])}

    def stop(self) -> dict:
        return {"status": "stopped"}
