import json
import time
import random
import re
import logging
from datetime import datetime
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# =========================
# GLOBAL CONFIG (LOCKED)
# =========================
AMAZON_HOME = "https://www.amazon.in/"
MAX_PRODUCTS = 5
OUTPUT_FILE = "output.json"

# Human timing (weighted randomness)
WAIT_SHORT = (3, 6)
WAIT_LONG = (6, 10)
TYPE_DELAY = (0.12, 0.35)

# Selectors (normalized & safe)
SEARCH_BOX_XPATH = '//input[@id="twotabsearchtextbox"]'

SEARCH_RESULT_CARD = 'div[data-component-type="s-search-result"]'
SEARCH_RESULT_LINK = "h2 a.a-link-normal"

PRODUCT_TITLE = "#productTitle"
PRICE_PRIMARY = ".a-price .a-price-whole"
PRICE_FALLBACK = ".a-offscreen"
AVAILABILITY = "#availability span"


# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("run.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("amazon-human-scraper")


# =========================
# HUMAN BEHAVIOR PRIMITIVES
# =========================
def human_sleep(a, b):
    time.sleep(random.uniform(a, b))


def weighted_sleep():
    # favor middle of range, rare extremes
    r = random.random()
    if r < 0.7:
        human_sleep(4, 7)
    else:
        human_sleep(3, 10)


def human_scroll(driver):
    height = driver.execute_script("return document.body.scrollHeight")
    max_depth = random.uniform(0.3, 0.8) * height
    step = random.randint(150, 350)

    y = 0
    while y < max_depth:
        driver.execute_script(f"window.scrollTo(0, {y});")
        human_sleep(0.6, 1.4)
        y += step

    # mandatory scroll back up (random extent)
    back_up = random.uniform(0.1, 0.4) * height
    driver.execute_script(f"window.scrollTo(0, {back_up});")
    human_sleep(1.5, 3.0)


def human_type(element, text):
    make_mistake = random.choice([True, False])
    mistake_done = False

    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(*TYPE_DELAY))

        if make_mistake and not mistake_done and random.random() < 0.12:
            element.send_keys(random.choice("abcdefghijklmnopqrstuvwxyz"))
            time.sleep(random.uniform(0.2, 0.4))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.3, 0.6))
            mistake_done = True


# =========================
# RISK DETECTION (HARD STOP)
# =========================
def risk_detected(driver):
    page = driver.page_source.lower()
    signals = [
        "captcha",
        "enter the characters you see",
        "unusual traffic",
        "robot check",
    ]
    return any(s in page for s in signals)


def hard_stop(driver, reason):
    log.error(f"HARD STOP: {reason}")
    try:
        driver.quit()
    finally:
        raise SystemExit(reason)


# =========================
# BROWSER SETUP
# =========================
def build_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        },
    )
    return driver


# =========================
# UTIL
# =========================
def clean_amazon_url(href):
    if not href:
        return None
    href = href.split("/ref=")[0]
    return urljoin(AMAZON_HOME, href)


def safe_text(el):
    try:
        return el.text.strip()
    except Exception:
        return None


def handle_continue_shopping(driver, observe_seconds=4):
    end_time = time.time() + observe_seconds

    while time.time() < end_time:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, ".a-button-text")
            for btn in buttons:
                text = btn.text.strip().lower()
                if "continue" in text:
                    log.info("Continue shopping button detected")
                    time.sleep(random.uniform(2.3, 3.5))
                    btn.click()
                    time.sleep(random.uniform(2.0, 4.0))
                    return
        except Exception:
            pass

        # human-like idle, not tight polling
        time.sleep(random.uniform(0.6, 1.2))


# =========================
# MAIN FLOW
# =========================
def run(query):
    driver = build_driver()
    wait = WebDriverWait(driver, 20)
    results = []
    session_meta = {
        "search_query": query,
        "search_time": datetime.utcnow().isoformat(),
        "marketplace": "amazon.in",
    }

    try:
        log.info("Opening Amazon homepage")
        driver.get(AMAZON_HOME)
        human_sleep(4, 8)

        handle_continue_shopping(driver)

        human_scroll(driver)

        if risk_detected(driver):
            hard_stop(driver, "Risk detected on homepage")

        log.info("Typing search query")
        search = wait.until(
            EC.presence_of_element_located((By.XPATH, SEARCH_BOX_XPATH))
        )
        search.click()
        human_type(search, query)
        human_sleep(2, 6)
        search.send_keys(Keys.ENTER)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_RESULT_CARD))
        )
        human_scroll(driver)

        if risk_detected(driver):
            hard_stop(driver, "Risk detected on results page")

            # =========================
            # COLLECT PRODUCT URLS
            # =========================
        cards = driver.find_elements(By.CSS_SELECTOR, SEARCH_RESULT_CARD)

        product_urls = []

        for card in cards:
            if len(product_urls) >= MAX_PRODUCTS:
                break

            asin = card.get_attribute("data-asin")
            if not asin:
                continue

            link_elements = card.find_elements(
                By.CSS_SELECTOR, "a[href*='/dp/'], a[href*='/sspa/click']"
            )

            if not link_elements:
                continue

            url = clean_amazon_url(link_elements[0].get_attribute("href"))
            if url:
                product_urls.append(url)

        log.info(f"Collected {len(product_urls)} product URLs")

        # =========================
        # VISIT PRODUCT PAGES
        # =========================
        for idx, product_url in enumerate(product_urls, 1):
            log.info(f"Opening product {idx}")
            driver.get(product_url)

            weighted_sleep()
            human_scroll(driver)

            if risk_detected(driver):
                hard_stop(driver, "Risk detected on product page")

            title = safe_text(
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_TITLE))
                )
            )

            price = None
            try:
                price = safe_text(driver.find_element(By.CSS_SELECTOR, PRICE_FALLBACK))
            except Exception:
                pass

            availability = None
            try:
                availability = safe_text(
                    driver.find_element(By.CSS_SELECTOR, AVAILABILITY)
                )
            except Exception:
                pass

            results.append(
                {
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "url": product_url,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            human_sleep(4, 7)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"session": session_meta, "products": results},
                f,
                indent=2,
                ensure_ascii=False,
            )

        log.info(f"Saved {len(results)} products to {OUTPUT_FILE}")

    except (TimeoutException, WebDriverException) as e:
        hard_stop(driver, f"Exception: {e}")

    finally:
        try:
            driver.quit()
        except Exception:
            pass


# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    q = "iphone 17"  # dummy test query
    run(q)
