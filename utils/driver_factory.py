"""Creates the WebDriver. Selenium 4.6+ downloads the matching driver itself (Selenium Manager)."""
from selenium import webdriver

from config import settings

# The demo site is covered in Google ad overlays that intercept clicks during
# signup/login. Blocking the ad hosts at network level (Chromium only) removes
# the problem at its source; BasePage.remove_ads() is the second line of defence.
_BLOCKED_URLS = [
    "*googlesyndication.com*", "*doubleclick.net*", "*googleadservices.com*",
    "*adservice.google.*", "*pagead2.*", "*fundingchoicesmessages.google.com*",
    "*google-analytics.com*", "*googletagmanager.com*",
]


def _block_ads(driver):
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": _BLOCKED_URLS})
    except Exception:  # Firefox has no CDP; the JS ad-remover still covers it
        pass


def create_driver():
    browser = settings.BROWSER

    if browser in ("chrome", "edge"):
        options = webdriver.ChromeOptions() if browser == "chrome" else webdriver.EdgeOptions()
        if settings.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.page_load_strategy = "eager"          # don't wait for slow ad/tracker requests
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,        # no "save password?" bubble
            "profile.password_manager_enabled": False,
        })
        driver = webdriver.Chrome(options=options) if browser == "chrome" else webdriver.Edge(options=options)
        _block_ads(driver)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if settings.HEADLESS:
            options.add_argument("-headless")
        options.page_load_strategy = "eager"
        driver = webdriver.Firefox(options=options)

    else:
        raise ValueError(f"Unsupported BROWSER '{browser}' (use chrome, firefox or edge)")

    driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
    if not settings.HEADLESS:
        driver.maximize_window()
    return driver
