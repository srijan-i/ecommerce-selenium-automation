"""Self-contained HTML execution report. Screenshots are embedded (base64), so the
single .html file can be e-mailed or archived without a screenshots folder."""
import base64
import html
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

_CSS = """
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f4f5f7;color:#222}
.wrap{max-width:1200px;margin:0 auto;padding:28px}
h1{margin:0 0 6px}h2{margin:28px 0 10px}
.banner{padding:14px 20px;border-radius:8px;color:#fff;font-size:20px;font-weight:600;margin:16px 0}
.PASSED{background:#2e7d32}.FAILED{background:#c62828}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px}
.card{background:#fff;border-radius:8px;padding:12px 20px;box-shadow:0 1px 3px #0002;min-width:110px}
.card b{display:block;font-size:24px}
table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 3px #0002}
th,td{padding:10px 12px;border-bottom:1px solid #e5e5e5;text-align:left;vertical-align:top;font-size:14px}
th{background:#263238;color:#fff}
.badge{padding:2px 10px;border-radius:12px;color:#fff;font-weight:600;font-size:12px}
.PASS{background:#2e7d32}.FAIL{background:#c62828}.WARN{background:#ef6c00}
.passed{background:#2e7d32}.failed{background:#c62828}.skipped{background:#757575}
details summary{cursor:pointer;color:#1565c0}
details img{max-width:520px;border:1px solid #ccc;margin-top:8px}
.meta td:first-child{font-weight:600;width:200px}
"""


@dataclass
class StepResult:
    name: str
    status: str                      # PASS | FAIL | WARN
    details: str = ""
    screenshot: Optional[str] = None
    duration: float = 0.0


@dataclass
class TestResult:
    name: str
    outcome: str                     # passed | failed | skipped
    message: str = ""
    duration: float = 0.0


class ExecutionReport:
    def __init__(self, title, meta=None):
        self.title = title
        self.meta = dict(meta or {})
        self.steps = []
        self.tests = []
        self.started = datetime.now()

    def add_step(self, name, status, details="", screenshot=None, duration=0.0):
        self.steps.append(StepResult(name, status, details, screenshot, duration))

    def add_test_result(self, name, outcome, message="", duration=0.0):
        self.tests.append(TestResult(name, outcome, message, duration))

    @property
    def overall(self):
        failed = any(s.status == "FAIL" for s in self.steps) or \
                 any(t.outcome == "failed" for t in self.tests)
        return "FAILED" if failed else "PASSED"

    @staticmethod
    def _screenshot_html(path):
        if not path or not Path(path).exists():
            return ""
        data = base64.b64encode(Path(path).read_bytes()).decode()
        return f'<details><summary>View</summary><img alt="screenshot" src="data:image/png;base64,{data}"></details>'

    def write(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        e = html.escape
        finished = datetime.now()
        count = lambda status: sum(1 for s in self.steps if s.status == status)

        meta = dict(self.meta)
        meta["Started"] = self.started.strftime("%Y-%m-%d %H:%M:%S")
        meta["Finished"] = finished.strftime("%Y-%m-%d %H:%M:%S")
        meta["Total duration"] = f"{(finished - self.started).total_seconds():.1f}s"

        out = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{e(self.title)}</title>",
               f"<style>{_CSS}</style></head><body><div class='wrap'>",
               f"<h1>{e(self.title)}</h1>",
               f"<div class='banner {self.overall}'>Overall result: {self.overall}</div>",
               "<div class='cards'>",
               f"<div class='card'><b>{len(self.steps)}</b>Steps</div>",
               f"<div class='card'><b style='color:#2e7d32'>{count('PASS')}</b>Passed</div>",
               f"<div class='card'><b style='color:#c62828'>{count('FAIL')}</b>Failed</div>",
               f"<div class='card'><b style='color:#ef6c00'>{count('WARN')}</b>Warnings</div></div>",
               "<h2>Run details</h2><table class='meta'>"]
        out += [f"<tr><td>{e(str(k))}</td><td>{e(str(v))}</td></tr>" for k, v in meta.items()]
        out.append("</table>")

        if self.tests:
            out.append("<h2>Test results</h2><table><tr><th>Test</th><th>Outcome</th><th>Duration</th><th>Message</th></tr>")
            out += [f"<tr><td>{e(t.name)}</td><td><span class='badge {t.outcome}'>{t.outcome.upper()}</span></td>"
                    f"<td>{t.duration:.1f}s</td><td>{e(t.message)}</td></tr>" for t in self.tests]
            out.append("</table>")

        out.append("<h2>Execution steps</h2><table><tr><th>Step</th><th>Status</th><th>Time</th>"
                   "<th>Details</th><th>Screenshot</th></tr>")
        out += [f"<tr><td>{e(s.name)}</td><td><span class='badge {s.status}'>{s.status}</span></td>"
                f"<td>{s.duration:.1f}s</td><td>{e(s.details)}</td><td>{self._screenshot_html(s.screenshot)}</td></tr>"
                for s in self.steps]
        out.append("</table></div></body></html>")

        path.write_text("".join(out), encoding="utf-8")
        return path
