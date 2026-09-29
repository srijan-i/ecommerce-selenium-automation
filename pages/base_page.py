import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoAlertPresentException,
    StaleElementReferenceException,
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config import settings

# Google ad containers that overlay the page and swallow clicks on the demo site.
AD_SELECTORS = [
    "ins.adsbygoogle", "iframe[id^='aswift']", "iframe[id^='google_ads']",
    "#google_vignette", ".google-auto-placed", "[id^='div-gpt-ad']",
]

_REMOVE_ADS_JS = """
arguments[0].forEach(sel => document.querySelectorAll(sel).forEach(el => el.remove()));
if (location.hash === '#google_vignette') {
    history.replaceState(null, '', location.pathname + location.search);
}
document.body.style.overflow = 'auto';
"""


class BasePage:
    """Reliable Selenium primitives shared by every page object."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.EXPLICIT_WAIT)

    # ---------- navigation / popups ----------
    def open(self, path=""):
        try:
            self.driver.get(f"{settings.BASE_URL}{path}")
        except TimeoutException:
            self.driver.execute_script("window.stop();")   # ads can stall the load; the page is usable
        self.remove_ads()

    def remove_ads(self):
        """Deletes ad overlays that would intercept clicks. Never raises."""
        try:
            self.driver.execute_script(_REMOVE_ADS_JS, AD_SELECTORS)
        except WebDriverException:
            pass

    def accept_alert(self, timeout=1):
        """Accepts a native browser alert/confirm if one is showing. Returns its text or None."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except (TimeoutException, NoAlertPresentException):
            return None

    # ---------- waiting / finding ----------
    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout) if timeout else self.wait

    def presence(self, locator, timeout=None):
        return self._wait(timeout).until(EC.presence_of_element_located(locator))

    def visible(self, locator, timeout=None, message=None):
        return self._wait(timeout).until(EC.visibility_of_element_located(locator), message or
                                         f"Element not visible: {locator}")

    def is_visible(self, locator, timeout=3):
        try:
            self.visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def text_of(self, locator, timeout=None):
        return self.visible(locator, timeout).text.strip()

    def scroll_to(self, locator):
        try:
            element = self.driver.find_element(*locator)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        except WebDriverException:
            pass

    # ---------- actions ----------
    def click(self, locator, timeout=None):
        """Normal click; on interception removes ads + rescrolls and retries; JS click as last resort."""
        self.pause()
        for _ in range(3):
            try:
                self._wait(timeout).until(EC.element_to_be_clickable(locator)).click()
                return
            except (ElementClickInterceptedException, ElementNotInteractableException,
                    StaleElementReferenceException):
                self.remove_ads()
                self.scroll_to(locator)
            except UnexpectedAlertPresentException:
                self.accept_alert()
        self.driver.execute_script("arguments[0].click();", self.presence(locator))

    def type_text(self, locator, text):
        self.pause()
        for attempt in range(3):
            try:
                element = self.visible(locator)
                self.scroll_to(locator)
                element.clear()
                element.send_keys(str(text))
                return
            except (ElementNotInteractableException, ElementClickInterceptedException,
                    StaleElementReferenceException):
                if attempt == 2:
                    raise
                self.remove_ads()

    def select_by_text(self, locator, text):
        self.pause()
        Select(self.visible(locator)).select_by_visible_text(str(text))

    def select_by_value(self, locator, value):
        self.pause()
        Select(self.visible(locator)).select_by_value(str(value))

    def pause(self, seconds=None):
        delay = settings.STEP_DELAY if seconds is None else seconds
        if delay > 0:
            time.sleep(delay)
