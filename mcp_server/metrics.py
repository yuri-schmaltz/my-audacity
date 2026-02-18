import time
import logging
from functools import wraps
from typing import Dict, List

import re

logger = logging.getLogger("audacity-mcp.metrics")

def redact_path(text: str) -> str:
    """Redacts absolute paths in logs to prevent PII leakage."""
    # Pattern to match Linux/Windows absolute paths
    path_pattern = r'(/[a-zA-Z0-9\._\-]+)+|([A-Z]:\\[a-zA-Z0-9\._\- \\]+)'
    return re.sub(path_pattern, "[REDACTED_PATH]", text)

# Simple in-memory metrics store
class Metrics:
    def __init__(self):
        self.latencies: List[float] = []
        self.errors = 0
        self.total_calls = 0

    def add_call(self, duration: float, success: bool):
        self.latencies.append(duration)
        self.total_calls += 1
        if not success:
            self.errors += 1

    def get_p95(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    def get_summary(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "errors": self.errors,
            "error_rate": (self.errors / self.total_calls) if self.total_calls > 0 else 0,
            "p95_latency_ms": self.get_p95() * 1000
        }

metrics = Metrics()

def track_performance(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        success = True
        try:
            result = f(*args, **kwargs)
            if isinstance(result, str) and result.startswith("Error"):
                success = False
            return result
        except Exception:
            success = False
            raise
        finally:
            duration = time.perf_counter() - start_time
            metrics.add_call(duration, success)
            safe_name = redact_path(f.__name__)
            logger.debug(f"Command {safe_name} took {duration:.4f}s (success={success})")
    return wrapper
