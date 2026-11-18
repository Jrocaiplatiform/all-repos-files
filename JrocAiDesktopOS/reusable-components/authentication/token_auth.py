import hashlib, hmac, secrets, time
from pathlib import Path

class InternalTokenAuth:
    def __init__(self, secret_file: Path):
        self.secret_path = Path(secret_file)
        self.secret_path.parent.mkdir(parents=True, exist_ok=True)
        if self.secret_path.exists():
            self._secret = self.secret_path.read_bytes().strip()
        else:
            self._secret = secrets.token_hex(32).encode("utf-8")
            self.secret_path.write_bytes(self._secret)

    def issue_token(self, service_id: str, role: str = "system", ttl: int = 3600) -> str:
        exp = int(time.time()) + ttl
        payload = f"{service_id}:{role}:{exp}"
        sig = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    def verify_token(self, token: str):
        parts = token.split(":")
        if len(parts) != 4:
            return None
        sid, role, exp_s, sig = parts
        if time.time() > int(exp_s):
            return None
        payload = f"{sid}:{role}:{exp_s}"
        expected = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        return {"service_id": sid, "role": role} if hmac.compare_digest(sig, expected) else None