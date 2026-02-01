"""Logging utilities for text2speech."""

import logging
import re


class SensitiveDataFilter(logging.Filter):
    """Redact sensitive data from logs."""

    PATTERNS = [
        (r"sk_[a-zA-Z0-9]{20,}", "sk_***REDACTED***"),
        (r'"api_key":\s*"[^"]+', '"api_key": "***"'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to redact sensitive information."""
        if not isinstance(record.msg, str):
            return True

        msg = record.msg
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg)
        record.msg = msg
        return True
