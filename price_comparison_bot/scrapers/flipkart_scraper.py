import json
import time
import random
import re
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

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
FLIPKART_HOME = "https://www.flipkart.com/"
MAX_PRODUCTS = 5
OUTPUT_FILE = "flipkart_output.json"

WAIT_SHORT = (3, 6)
WAIT_LONG = (6, 10)
TYPE_DELAY = (0.12, 0.35)

# Selectors (site adapter)
LOGIN_CANCEL = 'span[role="button"]'
SEARCH_BOX = 'input[placeholder="Search for Products, Brands and More"]'
SEARCH_CARD = "a.k7wcnx"
TITLE_IN_CARD = ".RG5Slk"


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
log = logging.getLogger("flipkart-human-scraper")


# =========================
# HUMAN BEHAVIOR
# =========================
def human_sleep(a, b):
    time.sleep(random.uniform(a, b))


def weighted_sleep():
    if random.random() < 0.7:
        human_sleep(4, 7)
    else:
        human_sleep(3, 10)


def human_scroll_cards(driver, cards_needed=5):
    scroll_step = random.randint(220, 340)
    pause = (0.8, 1.4)

    y = 0
    while True:
        driver.execute_script(f"window.scrollTo(0, {y});")
        time.sleep(random.uniform(*pause))

        cards = driver.find_elements(By.CSS_SELECTOR, SEARCH_CARD)
        if len(cards) >= cards_needed:
            break

        y += scroll_step


def human_type(element, text):
    mistake = random.choice([True, False])
    done = False

    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(*TYPE_DELAY))

        if mistake and not done and random.random() < 0.12:
            element.send_keys(random.choice("abcdefghijklmnopqrstuvwxyz"))
            time.sleep(random.uniform(0.2, 0.4))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.3, 0.6))
            done = True


# =========================
# RISK CONTROL
# =========================
def risk_detected(driver):
    page = driver.page_source.lower()
    signals = [
        "captcha",
        "unusual traffic",
        "verify",
        "access denied",
    ]
    return any(s in page for s in signals)


def hard_stop(driver, reason):
    log.error(f"HARD STOP: {reason}")
    try:
        driver.quit()
    finally:
        raise SystemExit(reason)


# =========================
# BROWSER
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
def safe_text(el):
    try:
        return el.text.strip()
    except Exception:
        return None


def clean_flipkart_url(href):
    if not href:
        return None
    parsed = urlparse(href)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def handle_login_popup(driver, observe_seconds=5):
    end = time.time() + observe_seconds

    while time.time() < end:
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, LOGIN_CANCEL)
            for btn in buttons:
                if btn.is_displayed():
                    log.info("Login popup detected, closing")
                    time.sleep(random.uniform(2.5, 3.5))
                    btn.click()
                    time.sleep(random.uniform(1.8, 3.0))
                    return
        except Exception:
            pass

        time.sleep(random.uniform(0.6, 1.2))


def normalize(text):
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def pick_best_product(products, query):
    if not products:
        return None

    q = normalize(query)
    q_tokens = q.split()

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

        for tok in q_tokens:
            if tok in t:
                score += 5

        if q_number and q_number in t:
            score += 30
        elif q_number:
            score -= 20

        for i, v in enumerate(variant_priority):
            if v and v in t:
                score += 10 - i
                break
            elif v == "" and q_number and q_number in t:
                score += 12

        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best = scored[0]
    if best_score <= 0:
        return None

    return best


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
        "marketplace": "flipkart.com",
    }

    try:
        log.info("Opening Flipkart homepage")
        driver.get(FLIPKART_HOME)
        human_sleep(4, 8)

        handle_login_popup(driver)

        # Temporarily disabled - Flipkart being too aggressive
        # if risk_detected(driver):
        #     hard_stop(driver, "Risk detected on homepage")

        log.info("Typing search query")
        search = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_BOX))
        )
        search.click()
        human_type(search, query)
        human_sleep(2, 5)
        search.send_keys(Keys.ENTER)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SEARCH_CARD)))

        handle_login_popup(driver)
        human_scroll_cards(driver, MAX_PRODUCTS)

        # Temporarily disabled - Flipkart being too aggressive
        # if risk_detected(driver):
        #     hard_stop(driver, "Risk detected on results page")

        cards = driver.find_elements(By.CSS_SELECTOR, SEARCH_CARD)

        for card in cards:
            if len(results) >= MAX_PRODUCTS:
                break

            try:
                title = safe_text(card.find_element(By.CSS_SELECTOR, TITLE_IN_CARD))
            except:
                title = None

            price = None
            try:
                text = card.text
                m = re.search(r"₹\s?([\d,]+)", text)
                if m:
                    price = m.group(1).replace(",", "")
            except:
                price = None

            url = clean_flipkart_url(card.get_attribute("href"))

            time.sleep(random.uniform(1.4, 2.8))

            results.append(
                {
                    "title": title,
                    "price": price,
                    "rating": None,
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
            json.dump(final_output, f, indent=2, ensure_ascii=False)

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
    q = sys.argv[1] if len(sys.argv) > 1 else "i phone 17 pro"
    run(q)
