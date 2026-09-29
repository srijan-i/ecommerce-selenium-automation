"""Runs each automation step, screenshots it, times it and logs it to the report."""
import time
from contextlib import contextmanager
from pathlib import Path
from config import settings

from utils.helpers import safe_filename, short_error


class StepContext:
    """Yielded by `with steps.step(...) as s:` - set `s.details` to describe what happened."""
    def __init__(self):
        self.details = ""


class StepRunner:
    def __init__(self, driver, report, screenshot_dir):
        self.driver = driver
        self.report = report
        self.screenshot_dir = Path(screenshot_dir)
        self._counter = 0

    def _screenshot(self, label):
        try:
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            path = self.screenshot_dir / f"{safe_filename(label)}.png"
            self.driver.save_screenshot(str(path))
            return str(path)
        except Exception:
            return None

    @contextmanager
    def step(self, name, critical=True):
        """
        critical=True  -> a failure is logged as FAIL and re-raised (test stops).
        critical=False -> a failure is logged as WARN and swallowed (used for cleanup).
        """
        self._counter += 1
        label = f"{self._counter:02d}. {name}"
        context = StepContext()
        started = time.perf_counter()
        try:
            yield context
        except Exception as exc:
            status = "FAIL" if critical else "WARN"
            self.report.add_step(label, status, f"{type(exc).__name__}: {short_error(exc)}",
                                 self._screenshot(f"{label} {status}"), time.perf_counter() - started)
            if critical:
                raise
        else:
            time.sleep(settings.STEP_DELAY)
            self.report.add_step(label, "PASS", context.details,
                                 self._screenshot(label), time.perf_counter() - started)
