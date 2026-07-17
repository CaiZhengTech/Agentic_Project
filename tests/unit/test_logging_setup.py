"""Unit tests for the JSON log formatter — one-line {"ts","level","logger","msg"}
objects via stdlib logging, no new deps.
"""

import json
import logging

from triagedesk.logging_setup import JsonFormatter


def test_json_formatter_produces_parseable_json_with_required_keys():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="triagedesk.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )

    line = formatter.format(record)
    parsed = json.loads(line)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "triagedesk.test"
    assert parsed["msg"] == "hello world"
    assert "ts" in parsed


def test_json_formatter_reflects_record_level():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="triagedesk.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="boom",
        args=None,
        exc_info=None,
    )

    parsed = json.loads(formatter.format(record))

    assert parsed["level"] == "ERROR"
    assert parsed["msg"] == "boom"
