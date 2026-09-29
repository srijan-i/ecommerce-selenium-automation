"""Small pure-Python helpers (no Selenium imports, so they are easy to unit test)."""
import re


def parse_money(text):
    """'Rs. 1,500' -> 1500   |   'Rs. 499.50' -> 499.5"""
    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(text))
    if not match:
        raise ValueError(f"No amount found in {text!r}")
    value = float(match.group().replace(",", ""))
    return int(value) if value.is_integer() else value


def safe_filename(text):
    """Turns a step label into a safe file name."""
    return re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_")[:80] or "screenshot"


def short_error(exc, limit=600):
    """Selenium errors carry a huge stacktrace; keep only the readable first part."""
    message = str(exc).split("Stacktrace:")[0]
    message = " ".join(message.split())
    if not message:
        message = "(no message)"
    return message if len(message) <= limit else message[:limit] + "..."
