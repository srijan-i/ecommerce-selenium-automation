from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.helpers import parse_money


class CartPage(BasePage):
    TABLE = (By.ID, "cart_info_table")
    ROWS = (By.CSS_SELECTOR, "#cart_info_table tbody tr")

    def wait_loaded(self):
        self.wait.until(EC.url_contains("/view_cart"))
        self.visible(self.TABLE, message="Cart table not shown - the cart may be empty")

    def get_items(self):
        items = []
        for row in self.driver.find_elements(*self.ROWS):
            items.append({
                "name": row.find_element(By.CSS_SELECTOR, "td.cart_description h4 a").text.strip(),
                "price": parse_money(row.find_element(By.CSS_SELECTOR, "td.cart_price p").text),
                "quantity": int(row.find_element(By.CSS_SELECTOR, "td.cart_quantity button").text.strip()),
                "total": parse_money(row.find_element(By.CSS_SELECTOR, "td.cart_total p").text),
            })
        return items
