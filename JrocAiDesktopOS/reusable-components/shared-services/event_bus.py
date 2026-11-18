import threading, uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class SystemEvent:
    topic: str
    source_layer: str
    payload: dict
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)
        self._history = []
        self._lock = threading.RLock()

    def subscribe(self, topic: str, fn):
        with self._lock:
            self._subs[topic].append(fn)

    def publish(self, topic: str, source_layer: str, payload: dict):
        ev = SystemEvent(topic=topic, source_layer=source_layer, payload=payload)
        with self._lock:
            self._history.append(ev)
            handlers = list(self._subs.get(topic, []))
        for fn in handlers:
            fn(ev)
        return ev