from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class HomePage(BasePage):
    PRODUCTS_LINK = (By.CSS_SELECTOR, "a[href='/products']")
    SIGNUP_LOGIN_LINK = (By.CSS_SELECTOR, "a[href='/login']")
    LOGOUT_LINK = (By.CSS_SELECTOR, "a[href='/logout']")
    DELETE_ACCOUNT_LINK = (By.CSS_SELECTOR, "a[href='/delete_account']")
    LOGGED_IN_AS = (By.XPATH, "//a[contains(., 'Logged in as')]")
    ACCOUNT_DELETED = (By.CSS_SELECTOR, "h2[data-qa='account-deleted']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "a[data-qa='continue-button']")
    CONSENT_BUTTON = (By.CSS_SELECTOR, "button.fc-cta-consent")

    def open_site(self):
        self.open("/")
        self.dismiss_popups()
        self.visible(self.PRODUCTS_LINK)

    def dismiss_popups(self):
        """Handles the cookie-consent dialog, ad overlays and native alerts, whichever appear."""
        if self.is_visible(self.CONSENT_BUTTON, timeout=2):
            try:
                self.click(self.CONSENT_BUTTON)
            except WebDriverException:
                pass
        self.remove_ads()
        self.accept_alert(timeout=0.5)

    def go_to_signup_login(self):
        self.remove_ads()
        self.click(self.SIGNUP_LOGIN_LINK)
        self.wait.until(EC.url_contains("/login"))

    def go_to_products(self):
        self.remove_ads()
        self.click(self.PRODUCTS_LINK)
        self.wait.until(EC.url_contains("/products"))

    def is_logged_in(self):
        return self.is_visible(self.LOGGED_IN_AS, timeout=8)

    def logged_in_username(self):
        return self.text_of(self.LOGGED_IN_AS).replace("Logged in as", "").strip()

    def logout(self):
        self.click(self.LOGOUT_LINK)
        self.wait.until(EC.url_contains("/login"))

    def delete_account(self):
        self.click(self.DELETE_ACCOUNT_LINK)
        self.visible(self.ACCOUNT_DELETED)
        self.click(self.CONTINUE_BUTTON)
