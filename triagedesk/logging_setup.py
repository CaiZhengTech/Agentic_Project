"""Structured JSON logging — one-line {"ts", "level", "logger", "msg"} objects via
stdlib `logging`, no new deps. Applied at app startup when `settings.log_json` is true.
"""

import json
import logging
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload)


def configure_json_logging(level: int = logging.INFO) -> None:
    """Point the root logger at a single stdout handler emitting JSON lines."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
