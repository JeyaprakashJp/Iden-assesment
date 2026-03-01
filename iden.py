import json
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------- credentials ----------------
LOGIN_URL = "https://hiring.idenhq.com/"
CHALLENGE_URL = "https://hiring.idenhq.com/challenge"

USERNAME = os.getenv('USER_NAME') or "jjeyaprakash58@gmail.com"
PASSWORD = os.getenv('PASSWORD') or "MKYqT1k4"

path = os.getcwd()

data_dir = os.path.join(path, "data")
os.makedirs(data_dir, exist_ok=True)

STORAGE_STATE = os.path.join(data_dir, "Storage_state.json")
OUTPUT_FILE = os.path.join(data_dir, "products.json")  

HEADLESS = False
# ---------------------------------------


def session_is_valid(page):
    try:
        page.goto(CHALLENGE_URL, timeout=15000)
        page.wait_for_selector("table", timeout=5000)
        return True
    except PlaywrightTimeoutError:
        return False


def login(page, context):
    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(2)

    for selector in [
        "#email",
        "input[type='email']",
        "input[name='email']",
        "input[placeholder*='email']",
    ]:
        if page.query_selector(selector):
            page.fill(selector, USERNAME)
            break
    else:
        raise RuntimeError("Email field not found")

    for selector in [
        "#password",
        "input[type='password']",
        "input[name='password']",
        "input[placeholder*='password']",
    ]:
        if page.query_selector(selector):
            page.fill(selector, PASSWORD)
            break
    else:
        raise RuntimeError("Password field not found")

    for selector in [
        "button[type='submit']",
        "button:has-text('Login')",
        "button:has-text('Sign In')",
    ]:
        btn = page.query_selector(selector)
        if btn:
            btn.click()
            break
    else:
        raise RuntimeError("Submit button not found")

    page.wait_for_load_state("networkidle", timeout=15000)
    context.storage_state(path=STORAGE_STATE)


def navigate_to_product_table(page):
    page.wait_for_selector("input[type='email']", state="detached", timeout=60000)

    page.wait_for_selector("button:has-text('Launch Challenge')", timeout=60000).click()
    page.wait_for_selector("button:has-text('Menu')", timeout=30000).click()
    page.wait_for_selector("button:has-text('Data Tools')", timeout=30000).click()
    page.wait_for_selector("button:has-text('Inventory Management')", timeout=30000).click()
    page.wait_for_selector("button:has-text('Product Catalog')", timeout=30000).click()
    page.wait_for_selector("button:has-text('Load Product Data')", timeout=30000).click()

    page.wait_for_selector("div.infinite-table", timeout=60000)


def extract_table_data(page):
    seen_ids = set()

    # max_scrolls = []
    MAX_SCROLLS = 250
    STABLE_SCROLL_LIMIT = 5

    page.wait_for_selector("table tbody tr", timeout=60000)

    f = open(OUTPUT_FILE, "a", encoding="utf-8")

    last_total = 0
    stable_scrolls = 0
    total_written = 0
    # products = []
    
    for scroll_index in range(MAX_SCROLLS):
        rows = page.query_selector_all("table tbody tr")

        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) < 8:
                continue

            product_id = cells[0].inner_text().strip()
            if not product_id or product_id in seen_ids:
                continue

            seen_ids.add(product_id)

            f.write(json.dumps({
                "id": product_id,
                "name": cells[1].inner_text().strip(),
                "price": cells[2].inner_text().strip(),
                "manufacturer": cells[3].inner_text().strip(),
                "category": cells[4].inner_text().strip(),
                "last_updated": cells[5].inner_text().strip(),
                "size": cells[6].inner_text().strip(),
                "color": cells[7].inner_text().strip(),
                "sku": cells[8].inner_text().strip() if len(cells) > 8 else ""
            }) + "\n")

            total_written += 1

        print(f"Scroll {scroll_index + 1} — total written: {total_written}")

        if total_written == last_total:
            stable_scrolls += 1
        else:
            stable_scrolls = 0

        if stable_scrolls >= STABLE_SCROLL_LIMIT:
            break

        last_total = total_written

        try:
            page.eval_on_selector(
                "div.infinite-table",
                "(el) => el.scrollTop = el.scrollHeight"
            )
        except:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        time.sleep(1.5)

    f.close()
    print(f"Finished — total written: {total_written}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=500,
            executable_path="/usr/bin/brave-browser"
        )

        if os.path.exists(STORAGE_STATE):
            context = browser.new_context(
                storage_state=STORAGE_STATE,
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            if not session_is_valid(page):
                context = browser.new_context()
                page = context.new_page()
                login(page, context)
        else:
            context = browser.new_context()
            page = context.new_page()
            login(page, context)

        navigate_to_product_table(page)
        extract_table_data(page)

        browser.close()


if __name__ == "__main__":
    main()