"""
Loads test data from JSON *or* Excel and validates it.

Excel layout (sheet 1): column A = key, column B = value, row 1 = header.
Dotted keys become nested objects, so the Excel file and the JSON file produce
exactly the same dictionary, e.g.  `search.product_keyword | Dress`.
"""
import json
from pathlib import Path

import openpyxl

from config import settings

_NEW_USER_KEYS = [
    "name", "password", "day", "month", "year", "first_name", "last_name",
    "address", "country", "state", "city", "zipcode", "mobile",
]


def load_test_data(file_name=None):
    path = Path(file_name) if file_name and Path(file_name).is_absolute() else \
        settings.DATA_DIR / (file_name or settings.DATA_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Test data file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif suffix in (".xlsx", ".xlsm"):
        data = _read_excel(path)
    else:
        raise ValueError(f"Unsupported data file type: {suffix} (use .json or .xlsx)")

    validate_test_data(data)
    return data


def _read_excel(path):
    sheet = openpyxl.load_workbook(path, data_only=True).active
    data = {}
    for key, value in sheet.iter_rows(min_row=2, max_col=2, values_only=True):
        if key is None or not str(key).strip():
            continue
        _set_nested(data, str(key).strip(), _coerce(value))
    return data


def _coerce(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "false"):
            return lowered == "true"
    return value


def _set_nested(target, dotted_key, value):
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value


def validate_test_data(data):
    """Fails early with a readable list of everything that is wrong or missing."""
    problems = []
    mode = data.get("user_mode")

    if mode not in ("new", "existing"):
        problems.append("user_mode must be 'new' or 'existing'")

    if mode == "new":
        profile = data.get("new_user", {})
        problems += [f"new_user.{k} is empty" for k in _NEW_USER_KEYS
                     if not str(profile.get(k, "")).strip()]

    if mode == "existing":
        creds = data.get("existing_user", {})
        problems += [f"existing_user.{k} is empty (required when user_mode is 'existing')"
                     for k in ("email", "password") if not str(creds.get(k, "")).strip()]

    if not str(data.get("search", {}).get("product_keyword", "")).strip():
        problems.append("search.product_keyword is empty")

    try:
        if int(data["cart"]["quantity"]) < 1:
            raise ValueError
    except (KeyError, TypeError, ValueError):
        problems.append("cart.quantity must be a whole number >= 1")

    if problems:
        raise ValueError("Invalid test data:\n  - " + "\n  - ".join(problems))
