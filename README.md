# E-Commerce Purchase Flow Automation

End-to-end UI test automation built with **Selenium WebDriver**, **Python** and **pytest**, using the **Page Object Model**. It automates a complete customer journey on the public demo site [automationexercise.com](https://automationexercise.com): registering, logging in, searching for a product, adding it to the cart with a chosen quantity, and verifying the cart.

Every run produces a self-contained **HTML execution report** with per-step status, timings and embedded screenshots.

---

## Table of Contents

- [Features](#features)
- [Test Scenario](#test-scenario)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Running the Tests](#running-the-tests)
- [Test Data (JSON / Excel)](#test-data-json--excel)
- [Configuration](#configuration)
- [Watching the Run in Slow Motion](#watching-the-run-in-slow-motion)
- [Reports and Screenshots](#reports-and-screenshots)
- [Design Notes](#design-notes)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Full purchase flow**: register, logout, login, search, quantity update, add to cart, cart verification
- **Fresh user on every run**: a unique email is generated each time, so there are no stale credentials or "email already exists" errors
- **Page Object Model**: locators and actions live in `pages/`, test logic stays readable
- **Data driven**: test data comes from **JSON or Excel** (identical structure), validated before the run starts
- **Popup and alert handling**: cookie-consent dialog, Google ad overlays, native browser alerts and the "Added to cart" modal
- **Screenshots** captured at every step, plus at the exact point of any failure
- **HTML execution report**: one portable file with screenshots embedded
- **Cross-browser**: Chrome, Firefox and Edge, with headless mode
- **Slow-motion mode**: highlights each element and pauses so you can follow the run
- **Automatic cleanup**: the account created by the run is deleted afterwards
- **Offline unit tests** for data loading, validation, helpers and the report generator

## Test Scenario

| # | Step | What is verified |
|---|------|------------------|
| 1 | Launch browser and open the application | Page title, popups dismissed |
| 2 | Register a new user | Account form submitted, "Account Created" shown |
| 3 | Continue and logout | Auto-logged in after signup, then logged out |
| 4 | Login with the new credentials | "Logged in as ..." is displayed |
| 5 | Search for a product | Search results are returned |
| 6 | Open the first result | Product name and unit price captured |
| 7 | Update quantity and add to cart | Quantity field accepted, "Added" popup shown |
| 8 | Open the cart from the popup | Cart page loads |
| 9 | Verify cart details | Name, unit price, quantity and `price x quantity = total` all match |
| 10 | Cleanup | Test account deleted (best effort, never fails the test) |

Setting `user_mode` to `existing` skips registration and logs in with credentials you provide.

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Language |
| Selenium 4 | Browser automation (drivers are downloaded automatically by Selenium Manager) |
| pytest | Test runner and fixtures |
| openpyxl | Reading Excel test data |

## Project Structure

```
.
├── conftest.py                  # pytest fixtures (driver, steps, data) and report hooks
├── pytest.ini
├── requirements.txt
├── config/
│   └── settings.py              # URL, browser, headless, timeouts, slow-motion (env-overridable)
├── data/
│   ├── test_data.json           # test data (JSON)
│   └── test_data.xlsx           # same data (Excel)
├── pages/                       # Page Object Model
│   ├── base_page.py             # waits, retrying clicks, ad removal, alerts, dropdowns
│   ├── home_page.py
│   ├── auth_page.py             # login and signup
│   ├── products_page.py
│   └── cart_page.py
├── utils/
│   ├── driver_factory.py        # Chrome / Firefox / Edge setup
│   ├── data_reader.py           # JSON and Excel loading + validation
│   ├── user_factory.py          # unique user generation
│   ├── steps.py                 # step runner: timing, screenshots, logging
│   ├── report.py                # HTML report generator
│   └── helpers.py
└── tests/
    ├── test_purchase_flow.py    # the end-to-end scenario
    └── unit/
        └── test_utils.py        # fast offline unit tests
```

## Getting Started

### Prerequisites

- Python 3.9 or newer
- Google Chrome, Mozilla Firefox or Microsoft Edge installed
- Internet access (the application under test is public, and Selenium downloads the browser driver on first run)

### Installation

```bash
git clone <your-repository-url>
cd <repository-folder>

python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate.bat

pip install -r requirements.txt
```

## Running the Tests

```bash
# Everything (unit tests + browser flow)
pytest

# Only the browser flow
pytest tests/test_purchase_flow.py

# Only the fast unit tests (no browser needed)
pytest tests/unit
```

Options are passed as environment variables:

```bash
# macOS / Linux
HEADLESS=true pytest tests/test_purchase_flow.py
BROWSER=firefox pytest tests/test_purchase_flow.py
DATA_FILE=test_data.xlsx pytest tests/test_purchase_flow.py
```

```powershell
# Windows PowerShell
$env:HEADLESS="true"; pytest tests/test_purchase_flow.py
$env:BROWSER="edge"; pytest tests/test_purchase_flow.py
```

## Test Data (JSON / Excel)

`data/test_data.json` and `data/test_data.xlsx` hold the same information, so use whichever you prefer (`DATA_FILE=test_data.xlsx`). In Excel, column A is the key (dotted for nesting, e.g. `search.product_keyword`), column B is the value.

| Key | Description |
|-----|-------------|
| `user_mode` | `new` registers a fresh user each run (recommended). `existing` logs in with `existing_user.*` |
| `cleanup_account` | `true` deletes the account created by the run |
| `new_user.*` | Profile used to register (name, password, date of birth, address, ...). The email is generated. `month` must be the full name, e.g. `May` |
| `existing_user.email`, `existing_user.password` | Only used when `user_mode` is `existing` |
| `search.product_keyword` | Product to search for |
| `cart.quantity` | Quantity entered before "Add to cart" |

Missing or invalid values stop the run immediately with a list of everything that needs fixing.

## Configuration

All settings live in `config/settings.py` and can be overridden with environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER` | `chrome` | `chrome`, `firefox` or `edge` |
| `HEADLESS` | `false` | Run without a visible browser window |
| `DATA_FILE` | `test_data.json` | `test_data.json` or `test_data.xlsx` |
| `BASE_URL` | `https://automationexercise.com` | Application under test |
| `EXPLICIT_WAIT` | `20` | Seconds to wait for elements |
| `PAGE_LOAD_TIMEOUT` | `45` | Seconds to wait for page loads |
| `SLOW_MO` | `0` | Seconds to pause before every action (see below) |
| `STEP_PAUSE` | `0` | Seconds to pause after each finished step |

## Watching the Run in Slow Motion

By default the tests run at full speed. To follow along, set a delay:

```bash
# macOS / Linux
SLOW_MO=1 STEP_PAUSE=2 pytest tests/test_purchase_flow.py
```

```powershell
# Windows PowerShell
$env:SLOW_MO="1"; $env:STEP_PAUSE="2"; pytest tests/test_purchase_flow.py
```

- `SLOW_MO=1` outlines each element in red and waits 1 second before clicking, typing or choosing a dropdown value.
- `STEP_PAUSE=2` waits 2 seconds after every completed step.
- Do not combine with `HEADLESS=true`, as there is nothing to watch.

Slow motion only adds delay to the actions; it does not change what is tested.

## Reports and Screenshots

After each run:

- **`reports/execution_report.html`**: the latest report (a timestamped copy is also kept). It shows the overall result, per-step status, duration, details, and embedded screenshots. It is a single file, so it can be emailed or archived as is.
- **`screenshots/<run-id>/`**: one PNG per step, plus a `..._FAIL.png` at the point of any failure.

Both folders are git-ignored.

## Design Notes

- **Reliable signup and login.** The demo site shows full-page ad overlays that intercept clicks. The framework blocks ad hosts at network level (Chrome and Edge), removes ad containers before interacting, retries intercepted clicks, and falls back to a JavaScript click as a last resort.
- **Clear failures.** Login and signup wait for either success or the site's own error message, and raise `AuthError` with that text instead of timing out silently.
- **No shared credentials.** A unique user per run means the suite never depends on an account left over from a previous run.
- **Critical vs best-effort steps.** A failing step stops the test and is marked `FAIL`. Cleanup runs as best effort and is marked `WARN` if it fails, so it never hides the real result.
- **Faster page loads.** The `eager` page-load strategy stops slow ad and tracking requests from stalling the run.

## Troubleshooting

| Symptom | What to do |
|---------|-----------|
| A step failed | Open `reports/execution_report.html`. The failed step shows the error text and a screenshot of the browser at that moment |
| `Invalid test data: ...` | Fix the listed keys in the JSON or Excel file |
| `Login rejected ... incorrect` (in `existing` mode) | The credentials in `existing_user` do not match a real account |
| An element cannot be found | The site may have changed. Locators are class attributes at the top of each file in `pages/`, so update them in one place |
| Driver download fails | Selenium needs internet access the first time it fetches the browser driver |
| Run is too fast to follow | Use `SLOW_MO` and `STEP_PAUSE` (see above) |

## Disclaimer

This project automates a public demo site built for practising test automation. Do not point it at systems you do not own or have permission to test.
