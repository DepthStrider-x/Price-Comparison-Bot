import json
import logging
from datetime import datetime
from urllib.parse import urljoin
from datetime import datetime, UTC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

from selenium.webdriver.chrome.service import Service

# ================== CONFIG ================== #
BASE_URL = "https://www.reliancedigital.in/"
MAX_PRODUCTS = 5
OUTPUT_FILE = "reliance_digital_output.json"
MARKETPLACE = "reliancedigital.in"


# ================= LOGGING ================= #
LOG_FILE = "reliance_digital.log"

logger = logging.getLogger("reliance_digital")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

# Attach handlers (avoid duplicates)
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# ================== POPUP HANDLER ================== #
def close_optional_popup(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[normalize-space()="No thanks"]'))
        ).click()
        logger.info("Popup handled: 'No thanks' clicked")
    except TimeoutException:
        logger.debug("No popup detected")


# ================== DRIVER ================== #
def init_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Use manually installed ChromeDriver
    service = Service(r"C:\chromedriver\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    logger.info("Chrome driver initialized")
    return driver


# ================== SEARCH ================== #
def perform_search(driver, query):
    logger.info(f"Opening homepage: {BASE_URL}")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 20)

    close_optional_popup(driver)

    search_box = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//input[@aria-label="Search Products & Brands"]')
        )
    )

    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)

    logger.info(f"Search triggered for query: '{query}'")


# ================== PRODUCT PARSER ================== #
def parse_product(card):
    try:
        title = card.find_element(By.CLASS_NAME, "product-card-title").text.strip()
        price_text = card.find_element(By.CLASS_NAME, "price").text
        price = price_text.replace("₹", "").replace(",", "").strip()
        link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

        if not title or not price or not link:
            raise ValueError("Missing essential product fields")

        return {
            "title": title,
            "price": price,
            "link": link,
        }

    except Exception as e:
        raise ValueError(f"Product parse failed: {e}")


# ================== SCRAPER ================== #
def scrape_products(driver):
    wait = WebDriverWait(driver, 20)

    close_optional_popup(driver)

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-card")))

    cards = driver.find_elements(By.CLASS_NAME, "product-card")
    logger.info(f"Product cards detected: {len(cards)}")

    products = []

    for index, card in enumerate(cards[:MAX_PRODUCTS], start=1):
        try:
            product = parse_product(card)
            products.append(product)
            logger.info(f"Parsed product {index}: {product['title']}")
        except Exception as e:
            logger.warning(f"Skipping product {index}: {e}")

    logger.info(f"Total products scraped: {len(products)}")
    return products


# ================== SAVE ================== #
def save_to_json(query, products):
    payload = {
        "session": {
            "search_query": query,
            "search_time": datetime.now(UTC).isoformat(),
            "marketplace": MARKETPLACE,
        },
        "products": products,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved → {OUTPUT_FILE}")


# ================== RUNNER ================== #
def run(query):
    logger.info("===== Reliance Digital Scraper Started =====")
    driver = init_driver()

    try:
        perform_search(driver, query)
        products = scrape_products(driver)
        save_to_json(query, products)

    except WebDriverException as e:
        logger.error(f"Critical browser error: {e}")

    finally:
        driver.quit()
        logger.info("Browser closed cleanly")
        logger.info("===== Scraper Finished =====")


# ================== ENTRY ================== #
if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "iphone 17"
    run(q)
