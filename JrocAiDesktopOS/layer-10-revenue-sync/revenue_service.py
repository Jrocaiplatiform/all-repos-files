import hashlib, hmac
from pathlib import Path

class RevenueSyncService:
    layer_id = "layer-10-revenue-sync"
    service_name = "revenue-sync"
    FREE = {"local_tools", "local_models", "core_jbot"}
    PREMIUM = FREE | {"advanced_models", "advanced_swarms", "quantum_enterprise"}

    def __init__(self, root_dir: Path, secret: bytes, kernel):
        self._secret = secret
        self.kernel = kernel
        self.edition = "free"
        self.sales_cents = 0

    def start(self) -> dict:
        return {"edition": self.edition}

    def issue_license(self, licensee: str, edition: str = "premium") -> str:
        sig = hmac.new(self._secret, f"{licensee}:{edition}".encode(), hashlib.sha256).hexdigest()[0:16]
        return f"JROC-{edition.upper()}-{licensee}-{sig}"

    def activate_license(self, licensee: str, edition: str, key: str) -> bool:
        if hmac.compare_digest(self.issue_license(licensee, edition), key):
            self.edition = edition.lower()
            return True
        return False

    def has_feature(self, feat: str) -> bool:
        return feat in (self.PREMIUM if self.edition == "premium" else self.FREE)

    def health_check(self) -> dict:
        return {"edition": self.edition}

    def stop(self) -> dict:
        return {"status": "stopped"}
