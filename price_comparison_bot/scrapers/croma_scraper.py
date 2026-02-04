import json
import logging
import time
from datetime import datetime, UTC
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


import requests

# ================= CONFIG ================= #
BASE_URL = "https://www.croma.com"
API_URL = "https://api.croma.com/searchservices/v1/search"
MAX_PRODUCTS = 5
OUTPUT_FILE = "croma_output.json"
TIMEOUT = 10

# ================= LOGGING ================= #
LOG_FILE = "croma.log"

logger = logging.getLogger("croma")
logger.setLevel(logging.INFO)
logger.propagate = False  # 🔥 CRITICAL

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

# Clear any existing handlers (important in reused sessions)
logger.handlers.clear()

# Console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def create_http_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    return session


# ================= HEADERS ================= #
HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/143.0.0.0 Safari/537.36"
    ),
    "accept": "application/json",
    "referer": "https://www.croma.com/",
    "origin": "https://www.croma.com",
}


# ================= NORMALIZER ================= #
def normalize_model(title: str) -> str:
    t = title.lower()
    if "pro max" in t:
        return "iphone_17_pro_max"
    if "pro" in t:
        return "iphone_17_pro"
    if "plus" in t:
        return "iphone_17_plus"
    return "iphone_17"


# ================= FETCH ================= #
def fetch_products(session: requests.Session, query: str):
    params = {
        "currentPage": 0,
        "query": f"{query}:relevance",
        "fields": "FULL",
        "channel": "WEB",
        "channelCode": "400049",
        "spellOpt": "DEFAULT",
    }

    logger.info(f"Calling Croma API for query: '{query}'")

    response = session.get(
        API_URL,
        params=params,
        timeout=TIMEOUT,
    )

    response.raise_for_status()
    return response.json()


# ================= PARSE ================= #
def parse_products(data: dict):
    products = []

    for item in data.get("products", [])[:MAX_PRODUCTS]:
        try:
            title = item["name"].strip()
            price = f"{item['price']['value']:.2f}"
            mrp = f"{item['mrp']['value']:.2f}"
            link = urljoin(BASE_URL, item["url"])
            image = item.get("plpImage")

            products.append(
                {
                    "title": title,
                    "price": price,
                    "mrp": mrp,
                    "link": link,
                    "image": image,
                    "normalized_model": normalize_model(title),
                }
            )

            logger.info(f"Parsed product: {title}")

        except Exception as e:
            logger.warning(f"Skipped product due to error: {e}")

    return products


# ================= SAVE ================= #
def save_output(query: str, products: list):
    payload = {
        "session": {
            "search_query": query,
            "search_time": datetime.now(UTC).isoformat(),
            "marketplace": "croma.com",
        },
        "products": products,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(products)} products → {OUTPUT_FILE}")


# ================= MAIN ================= #
def run(query: str):
    logger.info("===== Croma API Scraper Started =====")

    try:
        session = create_http_session()
        raw_data = fetch_products(session, query)

        products = parse_products(raw_data)
        save_output(query, products)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    finally:
        logger.info("===== Scraper Finished =====")


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "iphone 17"
    run(q)
