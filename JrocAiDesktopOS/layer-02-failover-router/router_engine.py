import json
import urllib.error
import urllib.request
from pathlib import Path


class FailoverRouterService:
    """Local-only Ollama route and inference adapter."""

    layer_id = "layer-02-failover-router"
    service_name = "failover-router"

    def __init__(self, root_dir: Path, kernel, model: str = "llama3.2"):
        self.root_dir = Path(root_dir)
        self.kernel = kernel
        self.model = model
        self.endpoint = "http://127.0.0.1:11434"

    def start(self) -> dict:
        return {"status": "ready", "mode": "local-only", "provider": "ollama", "model": self.model}

    def select_provider(self) -> dict:
        return {
            "selected": f"ollama/{self.model}",
            "provider": "ollama",
            "api_base": self.endpoint,
            "mode": "local-only",
            "external_fallback": False,
        }

    def generate(self, prompt: str, system_prompt: str = "You are J-BOT, the J-ROC AI assistant.") -> dict:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.endpoint}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
            content = result.get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                return {"ok": False, "error": "Local model returned an empty response"}
            return {"ok": True, "model": self.model, "reply": content}
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
            return {"ok": False, "error": f"Local inference unavailable: {exc}"}

    def health_check(self) -> dict:
        return {"status": "ready", "mode": "local-only", "model": self.model, "endpoint": self.endpoint}

    def stop(self) -> dict:
        return {"status": "stopped"}
