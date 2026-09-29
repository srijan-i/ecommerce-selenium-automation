"""Fast unit tests for everything that does not need a browser: `pytest tests/unit`"""
import json

import openpyxl
import pytest

from config import settings
from utils.data_reader import load_test_data, validate_test_data
from utils.helpers import parse_money, safe_filename, short_error
from utils.report import ExecutionReport
from utils.user_factory import build_new_user


def test_parse_money():
    assert parse_money("Rs. 500") == 500
    assert parse_money("Rs. 1,500") == 1500
    assert parse_money("Rs. 499.50") == 499.5
    with pytest.raises(ValueError):
        parse_money("free")


def test_safe_filename_and_short_error():
    assert safe_filename("01. Login / step") == "01_Login_step"
    assert short_error(Exception("boom\nStacktrace:\n  at foo")) == "boom"
    assert short_error(AssertionError()) == "(no message)"


def test_new_user_email_is_unique_and_profile_untouched():
    profile = {"email_prefix": "qa.user", "name": "X"}
    first, second = build_new_user(profile), build_new_user(profile)
    assert first["email"] != second["email"]
    assert first["email"].startswith("qa.user.") and first["email"].endswith("@example.com")
    assert "email" not in profile


def test_json_and_excel_data_are_identical():
    assert load_test_data("test_data.json") == load_test_data("test_data.xlsx")


def test_bundled_data_is_valid():
    data = load_test_data("test_data.json")
    assert data["user_mode"] == "new"
    assert int(data["cart"]["quantity"]) >= 1


def test_validation_reports_every_problem():
    bad = {"user_mode": "existing", "existing_user": {"email": "", "password": ""},
           "search": {"product_keyword": ""}, "cart": {"quantity": 0}}
    with pytest.raises(ValueError) as err:
        validate_test_data(bad)
    text = str(err.value)
    for expected in ("existing_user.email", "existing_user.password",
                     "search.product_keyword", "cart.quantity"):
        assert expected in text


def test_validation_rejects_unknown_mode():
    with pytest.raises(ValueError, match="user_mode"):
        validate_test_data({"user_mode": "bogus"})


def test_excel_types_are_coerced(tmp_path):
    src = json.loads((settings.DATA_DIR / "test_data.json").read_text())
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Key", "Value"])
    ws.append(["user_mode", "existing"])
    ws.append(["cleanup_account", "TRUE"])
    ws.append(["existing_user.email", "a@b.com"])
    ws.append(["existing_user.password", "pw"])
    ws.append(["search.product_keyword", "Top"])
    ws.append(["cart.quantity", 2.0])
    path = tmp_path / "d.xlsx"
    wb.save(path)
    data = load_test_data(str(path))
    assert data["cleanup_account"] is True
    assert data["cart"]["quantity"] == 2 and isinstance(data["cart"]["quantity"], int)
    assert src["search"]["product_keyword"] == "Dress"


def test_report_is_self_contained_html(tmp_path):
    shot = tmp_path / "s.png"
    shot.write_bytes(b"\x89PNG\r\n\x1a\n")
    report = ExecutionReport("Demo <report>", meta={"Browser": "chrome"})
    report.add_step("01. Login", "PASS", "ok <b>", str(shot), 1.2)
    report.add_step("02. Search", "FAIL", "AssertionError: nothing found", None, 0.4)
    report.add_test_result("test_flow", "failed", "boom", 3.0)
    path = report.write(tmp_path / "out" / "r.html")
    html = path.read_text(encoding="utf-8")
    assert report.overall == "FAILED"
    assert "data:image/png;base64," in html          # screenshot embedded
    assert "Demo &lt;report&gt;" in html and "ok &lt;b&gt;" in html   # escaped
    assert "AssertionError: nothing found" in html
