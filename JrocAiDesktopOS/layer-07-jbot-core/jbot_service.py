from pathlib import Path


class JBotCoreService:
    layer_id = "layer-07-jbot-core"
    service_name = "jbot-core"

    def __init__(self, root_dir: Path, router, vault, swarms, kernel):
        self.root_dir = Path(root_dir)
        self.router = router
        self.vault = vault
        self.swarms = swarms
        self.kernel = kernel

    def start(self) -> dict:
        return {
            "status": "ready",
            "legacy_engine": (self.root_dir / "layer-07-jbot-core" / "jroc_core_engine.py").exists(),
            "inference_mode": "local-only",
        }

    def ask(self, prompt: str) -> dict:
        if not isinstance(prompt, str) or not prompt.strip():
            return {"ok": False, "status": "INVALID_PROMPT", "error": "Prompt is required"}
        prompt = prompt.strip()
        route = self.router.select_provider()
        self.vault.put("jbot.last_prompt", prompt, namespace="history")
        result = self.router.generate(prompt)
        if not result.get("ok"):
            self.kernel.publish(
                "jbot.prompt_queued",
                self.layer_id,
                {"provider": route["selected"], "reason": result.get("error", "unavailable")},
            )
            return {
                "ok": False,
                "status": "LOCAL_MODEL_UNAVAILABLE",
                "route": route,
                "reply": "The prompt is saved in the local Vault. Start the approved local Ollama model and retry; no external AI service was contacted.",
            }
        self.kernel.publish("jbot.replied", self.layer_id, {"provider": route["selected"]})
        return {"ok": True, "status": "completed", "route": route, "reply": result["reply"]}

    def health_check(self) -> dict:
        return {"status": "ready", "inference_mode": "local-only"}

    def stop(self) -> dict:
        return {"status": "stopped"}
