"""
End-to-end purchase flow on https://automationexercise.com

  1. Launch browser, open site, dismiss popups
  2. (user_mode = "new")      Register a brand-new unique user -> logout
  3. Login                    (with the freshly registered user, or `existing_user`)
  4. Search product
  5. Open product, update quantity, add to cart (handles the "Added!" popup)
  6. Verify cart: name, unit price, quantity, line total
  7. Cleanup: delete the account this run created

Every step is timed, screenshotted and written to reports/execution_report.html.
"""
import pytest

from pages.auth_page import AuthPage
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from utils.user_factory import build_new_user

pytestmark = pytest.mark.e2e


def test_purchase_flow(driver, steps, test_data):
    home, auth = HomePage(driver), AuthPage(driver)
    products, cart = ProductsPage(driver), CartPage(driver)

    keyword = test_data["search"]["product_keyword"]
    quantity = int(test_data["cart"]["quantity"])
    created_account = None            # (email, password) once registration has succeeded

    try:
        with steps.step("Launch browser and open application") as s:
            home.open_site()
            assert "Automation Exercise" in driver.title, f"Unexpected page title: {driver.title!r}"
            s.details = f"Opened {driver.current_url} - title '{driver.title}'"

        # ---------- registration (fresh user every run) ----------
        if test_data["user_mode"] == "new":
            user = build_new_user(test_data["new_user"])
            credentials = (user["email"], user["password"])

            with steps.step("Register a new user") as s:
                home.go_to_signup_login()
                auth.start_signup(user["name"], user["email"])
                auth.fill_account_form(user)
                auth.submit_account_form()
                created_account = credentials
                s.details = f"Account created for {user['email']}"

            with steps.step("Continue after registration") as s:
                auth.continue_after_registration()
                assert home.is_logged_in(), "Not logged in after registration"
                s.details = f"Auto-logged in as '{home.logged_in_username()}'"

            with steps.step("Logout") as s:
                home.logout()
                assert "/login" in driver.current_url
                s.details = "Logged out; login page displayed"
        else:
            existing = test_data["existing_user"]
            credentials = (existing["email"], existing["password"])

        # ---------- login ----------
        with steps.step("Login") as s:
            if "/login" not in driver.current_url:
                home.go_to_signup_login()
            auth.login(*credentials)
            assert home.is_logged_in(), "Login form accepted but 'Logged in as' is not shown"
            s.details = f"Logged in as '{home.logged_in_username()}' ({credentials[0]})"

        # ---------- search ----------
        with steps.step("Search product") as s:
            home.go_to_products()
            products.search(keyword)
            found = products.result_count()
            assert found > 0, f"No products found for '{keyword}'"
            s.details = f"Search '{keyword}' returned {found} product(s)"

        # ---------- add to cart ----------
        with steps.step("Open first search result") as s:
            products.open_first_product()
            product = products.product_details()
            s.details = f"{product['name']} - unit price {product['price']}"

        with steps.step("Update quantity and add to cart") as s:
            products.set_quantity(quantity)
            products.add_to_cart()
            s.details = f"Quantity set to {quantity}; 'Added!' popup displayed"

        with steps.step("Open cart from popup") as s:
            products.open_cart_from_popup()
            cart.wait_loaded()
            s.details = "Cart page displayed"

        # ---------- verify ----------
        with steps.step("Verify cart details") as s:
            items = cart.get_items()
            assert items, "Cart is empty"
            item = next((i for i in items if i["name"].lower() == product["name"].lower()), None)
            assert item, f"'{product['name']}' not in cart. Cart holds: {[i['name'] for i in items]}"
            assert item["quantity"] == quantity, f"Quantity: expected {quantity}, cart shows {item['quantity']}"
            assert item["price"] == product["price"], f"Price: expected {product['price']}, cart shows {item['price']}"
            assert item["total"] == item["price"] * quantity, \
                f"Total: expected {item['price'] * quantity}, cart shows {item['total']}"
            s.details = (f"{item['name']} | price {item['price']} x qty {item['quantity']} "
                         f"= total {item['total']} (all values match)")

    finally:
        # Best-effort cleanup; a problem here is logged as a warning and never fails the test.
        if created_account and test_data.get("cleanup_account", True):
            with steps.step("Cleanup - delete test account", critical=False) as s:
                if not home.is_logged_in():
                    home.go_to_signup_login()
                    auth.login(*created_account)
                home.delete_account()
                s.details = f"Deleted {created_account[0]}"
