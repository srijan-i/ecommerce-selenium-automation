from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.helpers import parse_money


class ProductsPage(BasePage):
    SEARCH_INPUT = (By.ID, "search_product")
    SEARCH_BUTTON = (By.ID, "submit_search")
    SEARCH_TITLE = (By.XPATH, "//h2[contains(@class,'title') and normalize-space()='Searched Products']")
    RESULT_CARDS = (By.CSS_SELECTOR, ".features_items .product-image-wrapper")
    FIRST_VIEW_PRODUCT = (By.XPATH, "(//div[contains(@class,'features_items')]//a[contains(@href,'/product_details/')])[1]")

    DETAIL_NAME = (By.CSS_SELECTOR, ".product-information h2")
    DETAIL_PRICE = (By.CSS_SELECTOR, ".product-information span span")
    QUANTITY = (By.ID, "quantity")
    ADD_TO_CART = (By.CSS_SELECTOR, ".product-information button.cart")

    CART_MODAL = (By.ID, "cartModal")                                  # Bootstrap "Added!" popup
    MODAL_VIEW_CART = (By.CSS_SELECTOR, "#cartModal a[href='/view_cart']")

    def search(self, keyword):
        self.type_text(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
        self.visible(self.SEARCH_TITLE, message=f"'Searched Products' heading not shown for '{keyword}'")

    def result_count(self):
        return len(self.driver.find_elements(*self.RESULT_CARDS))

    def open_first_product(self):
        self.remove_ads()
        self.click(self.FIRST_VIEW_PRODUCT)
        self.wait.until(EC.url_contains("/product_details/"))

    def product_details(self):
        return {
            "name": self.text_of(self.DETAIL_NAME),
            "price": parse_money(self.text_of(self.DETAIL_PRICE)),
        }

    def set_quantity(self, quantity):
        self.type_text(self.QUANTITY, quantity)
        actual = self.visible(self.QUANTITY).get_attribute("value")
        if actual != str(quantity):
            raise AssertionError(f"Quantity field shows '{actual}' after typing '{quantity}'")

    def add_to_cart(self):
        self.click(self.ADD_TO_CART)
        self.visible(self.CART_MODAL, message="'Added to cart' popup did not appear")

    def open_cart_from_popup(self):
        self.click(self.MODAL_VIEW_CART)
        self.wait.until(EC.url_contains("/view_cart"))
