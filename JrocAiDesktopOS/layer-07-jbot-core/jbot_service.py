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
        return {"legacy_engine": (self.root_dir / "layer-07-jbot-core" / "jroc_core_engine.py").exists()}

    def ask(self, prompt: str) -> dict:
        route = self.router.select_provider()
        self.vault.put("jBot.last_prompt", prompt, namespace="history")
        self.kernel.publish("jbot.replied", self.layer_id, {"provider": route["selected"]})
        return {"route": route, "reply": f"[J-Bot Core] {prompt}"}

    def health_check(self) -> dict:
        return {"status": "ready"}

    def stop(self) -> dict:
        return {"status": "stopped"}
