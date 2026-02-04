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

from selenium.webdriver.chrome.service import Service


# =========================
# GLOBAL CONFIG (LOCKED)
# =========================
AMAZON_HOME = "https://www.amazon.in/"
MAX_PRODUCTS = 5
OUTPUT_FILE = "amazon_output.json"

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


def human_scroll_cards(driver, cards_needed=5):
    scroll_step = random.randint(220, 320)
    pause = (0.8, 1.4)

    y = 0
    while True:
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(random.uniform(*pause))

        cards = driver.find_elements(By.CSS_SELECTOR, SEARCH_RESULT_CARD)
        if len(cards) >= cards_needed:
            break

        y += scroll_step


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

    # Use manually installed ChromeDriver
    service = Service(r"C:\chromedriver\chromedriver-win64\chromedriver.exe")
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


def normalize(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def pick_best_product(products, query):
    if not products:
        return None

    q = normalize(query)
    q_tokens = q.split()

    # extract model number if present (15, 16, 17 etc.)
    q_number = None
    for t in q_tokens:
        if t.isdigit():
            q_number = t
            break

    variant_priority = ["", "pro", "plus", "max", "ultra"]

    scored = []

    for p in products:
        title = p.get("title") or ""
        t = normalize(title)

        score = 0

        # token overlap
        for tok in q_tokens:
            if tok in t:
                score += 5

        # exact number match
        if q_number and q_number in t:
            score += 30
        elif q_number:
            score -= 20  # hard penalty for wrong generation

        # variant preference
        for i, v in enumerate(variant_priority):
            if v and v in t:
                score += 10 - i
                break
            elif v == "" and q_number and q_number in t:
                score += 12

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    # reject garbage matches
    best_score, best_product = scored[0]
    if best_score <= 0:
        return None

    return best_product


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

        human_scroll_cards(driver, MAX_PRODUCTS)

        if risk_detected(driver):
            hard_stop(driver, "Risk detected on results page")

            # =========================
            # COLLECT PRODUCT URLS
            # =========================
        cards = driver.find_elements(By.CSS_SELECTOR, SEARCH_RESULT_CARD)

        for card in cards:
            if len(results) >= MAX_PRODUCTS:
                break

            try:
                title = safe_text(card.find_element(By.CSS_SELECTOR, "h2 span"))
            except:
                title = None

            # -------- PRICE EXTRACTION (CARD-SAFE) --------
            price = None

            try:
                # Primary: whole price (most reliable)
                whole = card.find_element(
                    By.CSS_SELECTOR, ".a-price-whole"
                ).text.strip()

                try:
                    fraction = card.find_element(
                        By.CSS_SELECTOR, ".a-price-fraction"
                    ).text.strip()
                except:
                    fraction = "00"

                price = f"{whole}.{fraction}"

            except:
                price = None
            # ---------------------------------------------

            try:
                rating = safe_text(card.find_element(By.CSS_SELECTOR, ".a-icon-alt"))
            except:
                rating = None

            try:
                link = card.find_element(By.CSS_SELECTOR, "a[href*='/dp/']")
                url = clean_amazon_url(link.get_attribute("href"))
            except:
                url = None

            time.sleep(random.uniform(1.5, 3.0))

            results.append(
                {
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "url": url,
                    "source": "search_card",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        best = pick_best_product(results, query)

        final_output = {
            "session": session_meta,
            "best_product": best,
            "all_products": results,
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                final_output,
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
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "iphone 17"
    run(q)
