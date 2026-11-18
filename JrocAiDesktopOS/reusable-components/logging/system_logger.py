import json, logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "layer": getattr(record, "layer", "system"),
            "component": record.name,
            "message": record.getMessage(),
        })

def get_system_logger(component: str, layer: str = "system"):
    base_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    base_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"jroc.{layer}.{component}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        fh = RotatingFileHandler(base_dir / "jroc_system.jsonl", maxBytes=5242880, backupCount=3, encoding="utf-8")
        fh.setFormatter(JsonFormatter())
        logger.addHandler(fh)
    return logging.LoggerAdapter(logger, {"layer": layer})