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
        return {"status": "ready", "approval_mode": "fail-closed"}

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
        # Caller-supplied role strings are not authenticated identities.
        return {
            "allowed": False,
            "reason": "Denied until authenticated identity and policy enforcement are integrated",
        }

    def approve_request(self, request_id: str, approved: bool, approved_by: str = "") -> dict:
        # Do not accept a caller-supplied "owner" label as proof of authority.
        return {
            "ok": False,
            "error": "Approval is disabled until verified Owner authentication is integrated",
        }

    def health_check(self) -> dict:
        return {
            "pending": sum(1 for item in self.approvals.values() if item["status"] == "pending"),
            "approval_mode": "fail-closed",
        }

    def stop(self) -> dict:
        return {"status": "stopped"}
