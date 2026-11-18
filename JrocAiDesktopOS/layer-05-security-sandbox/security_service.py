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
        if action in self.HIGH_RISK:
            request_id = uuid.uuid4().hex[:12]
            self.approvals[request_id] = {
                "id": request_id,
                "action": action,
                "status": "pending",
            }
            self.kernel.publish(
                "security.approval_required", self.layer_id, self.approvals[request_id]
            )
            return {
                "allowed": False,
                "requires_owner_approval": True,
                "request_id": request_id,
            }
        allowed = role in {"owner", "system", "kernel"}
        return {"allowed": allowed, "reason": "role policy"}

    def approve_request(self, request_id: str, approved: bool, approved_by: str) -> dict:
        if approved_by != "owner":
            return {"ok": False, "error": "Only the Owner may approve high-risk actions"}
        request = self.approvals.get(request_id)
        if request is None or request["status"] != "pending":
            return {"ok": False, "error": "Approval request not found or already decided"}
        request["status"] = "approved" if approved else "rejected"
        request["approved_by"] = approved_by
        self.kernel.publish("security.approval_decided", self.layer_id, dict(request))
        return {"ok": True, "status": request["status"]}

    def health_check(self) -> dict:
        return {
            "pending": sum(1 for item in self.approvals.values() if item["status"] == "pending")
        }

    def stop(self) -> dict:
        return {"status": "stopped"}
