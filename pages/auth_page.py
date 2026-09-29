from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class AuthError(Exception):
    """Raised with the site's own error text when login or signup is rejected."""


class AuthPage(BasePage):
    # login form
    LOGIN_EMAIL = (By.CSS_SELECTOR, "input[data-qa='login-email']")
    LOGIN_PASSWORD = (By.CSS_SELECTOR, "input[data-qa='login-password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[data-qa='login-button']")
    LOGIN_ERROR = (By.CSS_SELECTOR, "form[action='/login'] p")
    LOGGED_IN_AS = (By.XPATH, "//a[contains(., 'Logged in as')]")

    # first signup step (name + email)
    SIGNUP_NAME = (By.CSS_SELECTOR, "input[data-qa='signup-name']")
    SIGNUP_EMAIL = (By.CSS_SELECTOR, "input[data-qa='signup-email']")
    SIGNUP_BUTTON = (By.CSS_SELECTOR, "button[data-qa='signup-button']")
    SIGNUP_ERROR = (By.CSS_SELECTOR, "form[action='/signup'] p")

    # "Enter Account Information" form
    GENDER_MR = (By.ID, "id_gender1")
    GENDER_MRS = (By.ID, "id_gender2")
    PASSWORD = (By.ID, "password")
    DAYS = (By.ID, "days")
    MONTHS = (By.ID, "months")
    YEARS = (By.ID, "years")
    FIRST_NAME = (By.ID, "first_name")
    LAST_NAME = (By.ID, "last_name")
    COMPANY = (By.ID, "company")
    ADDRESS = (By.ID, "address1")
    COUNTRY = (By.ID, "country")
    STATE = (By.ID, "state")
    CITY = (By.ID, "city")
    ZIPCODE = (By.ID, "zipcode")
    MOBILE = (By.ID, "mobile_number")
    CREATE_ACCOUNT = (By.CSS_SELECTOR, "button[data-qa='create-account']")
    ACCOUNT_CREATED = (By.CSS_SELECTOR, "h2[data-qa='account-created']")
    CONTINUE_BUTTON = (By.CSS_SELECTOR, "a[data-qa='continue-button']")

    # ---------- login ----------
    def login(self, email, password):
        """Logs in; raises AuthError carrying the site's message if the credentials are rejected."""
        self.type_text(self.LOGIN_EMAIL, email)
        self.type_text(self.LOGIN_PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

        def outcome(driver):
            if driver.find_elements(*self.LOGGED_IN_AS):
                return ("ok", "")
            for el in driver.find_elements(*self.LOGIN_ERROR):
                if el.text.strip():
                    return ("error", el.text.strip())
            return False

        status, message = WebDriverWait(self.driver, 15).until(
            outcome, "Neither a logged-in state nor a login error appeared after clicking Login")
        if status == "error":
            raise AuthError(f"Login rejected for '{email}': {message}")

    # ---------- signup ----------
    def start_signup(self, name, email):
        """Submits name + email; raises AuthError if the site says the e-mail is already registered."""
        self.type_text(self.SIGNUP_NAME, name)
        self.type_text(self.SIGNUP_EMAIL, email)
        self.click(self.SIGNUP_BUTTON)

        def outcome(driver):
            if driver.find_elements(*self.DAYS):                      # only exists on the account form
                return ("ok", "")
            for el in driver.find_elements(*self.SIGNUP_ERROR):
                if el.text.strip():
                    return ("error", el.text.strip())
            return False

        status, message = WebDriverWait(self.driver, 15).until(
            outcome, "Neither the account form nor a signup error appeared after clicking Signup")
        if status == "error":
            raise AuthError(f"Signup rejected for '{email}': {message}")

    def fill_account_form(self, user):
        self.click(self.GENDER_MRS if str(user.get("title", "Mr")).lower() in ("mrs", "ms", "miss") else self.GENDER_MR)
        self.type_text(self.PASSWORD, user["password"])
        self.select_by_value(self.DAYS, int(user["day"]))
        self.select_by_text(self.MONTHS, user["month"])           # full month name, e.g. "May"
        self.select_by_value(self.YEARS, int(user["year"]))
        self.type_text(self.FIRST_NAME, user["first_name"])
        self.type_text(self.LAST_NAME, user["last_name"])
        if str(user.get("company", "")).strip():
            self.type_text(self.COMPANY, user["company"])
        self.type_text(self.ADDRESS, user["address"])
        self.select_by_text(self.COUNTRY, user["country"])
        self.type_text(self.STATE, user["state"])
        self.type_text(self.CITY, user["city"])
        self.type_text(self.ZIPCODE, user["zipcode"])
        self.type_text(self.MOBILE, user["mobile"])

    def submit_account_form(self):
        self.remove_ads()
        self.click(self.CREATE_ACCOUNT)
        self.visible(self.ACCOUNT_CREATED, timeout=20,
                     message="'ACCOUNT CREATED!' did not appear after submitting the form")

    def continue_after_registration(self):
        self.click(self.CONTINUE_BUTTON)
