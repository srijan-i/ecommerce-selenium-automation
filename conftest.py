"""Shared fixtures and the hooks that build the execution report."""
import shutil
from datetime import datetime

import pytest

from config import settings
from utils.data_reader import load_test_data
from utils.report import ExecutionReport
from utils.steps import StepRunner

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

EXEC_REPORT = ExecutionReport(
    title="E-Commerce Purchase Flow - Execution Report",
    meta={
        "Application": settings.BASE_URL,
        "Browser": settings.BROWSER + (" (headless)" if settings.HEADLESS else ""),
        "Test data file": settings.DATA_FILE,
        "Run id": RUN_ID,
    },
)


@pytest.fixture(scope="session")
def test_data():
    data = load_test_data()
    EXEC_REPORT.meta["User mode"] = data["user_mode"]
    return data


@pytest.fixture
def driver():
    from utils.driver_factory import create_driver      # imported lazily: unit tests need no Selenium
    browser = create_driver()
    yield browser
    browser.quit()


@pytest.fixture
def steps(driver):
    return StepRunner(driver, EXEC_REPORT, settings.SCREENSHOT_DIR / RUN_ID)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    if result.when == "call" or (result.when == "setup" and result.failed):
        message = ""
        if result.failed and call.excinfo is not None:
            message = str(call.excinfo.value).split("Stacktrace:")[0].strip()[:400]
        EXEC_REPORT.add_test_result(item.name, result.outcome, message, result.duration)


def pytest_sessionfinish(session, exitstatus):
    if not EXEC_REPORT.steps and not EXEC_REPORT.tests:
        return                                           # nothing ran (e.g. collection error)
    stamped = EXEC_REPORT.write(settings.REPORT_DIR / f"execution_report_{RUN_ID}.html")
    shutil.copyfile(stamped, settings.REPORT_DIR / "execution_report.html")
    print(f"\nExecution report : {settings.REPORT_DIR / 'execution_report.html'}")
    print(f"Screenshots      : {settings.SCREENSHOT_DIR / RUN_ID}")
