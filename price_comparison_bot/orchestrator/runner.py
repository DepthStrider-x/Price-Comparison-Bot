import sys
import subprocess
import json
import logging
import os
import time
from typing import List, Dict, Any

# Ensure we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils import matcher, exporter
except ImportError:
    # If running from root, this might be needed
    from price_comparison_bot.utils import matcher, exporter

# Configure Logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)
log = logging.getLogger("Orchestrator")

# Scraper Configurations
SCRAPERS = [
    {
        "name": "Flipkart",
        "script": "scrapers/flipkart_scraper.py",
        "output": "flipkart_output.json",
    },
    {
        "name": "Amazon",
        "script": "scrapers/amazon_scraper.py",
        "output": "amazon_output.json",
    },
    {
        "name": "Reliance",
        "script": "scrapers/reliance_scraper.py",
        "output": "reliance_digital_output.json",
    },
    {
        "name": "Croma",
        "script": "scrapers/croma_scraper.py",
        "output": "croma_output.json",
    },
]

def load_json(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log.error(f"Failed to load {filepath}: {e}")
    return None

def normalize_product(product, site_name):
    # Ensure common fields: title, price, url, image, site
    
    # Title
    title = product.get("title") or product.get("name") or "Unknown Product"
    
    # Price (clean it)
    price = product.get("price", "0")
    if price:
        # Remove currency symbols and commas, keep only digits and dots
        clean_price = "".join(c for c in str(price) if c.isdigit() or c == '.')
        # Handle cases with multiple dots (rare but possible) or empty
        price = clean_price if clean_price else "0"
    
    # URL
    url = product.get("url") or product.get("link") or "#"
    
    # Image
    image = product.get("image") or product.get("plpImage") or ""
    
    return {
        "title": title,
        "price": price,
        "url": url,
        "image": image,
        "site": site_name,
        "recommended": False
    }

def run_orchestrator(query):
    log.info(f"Starting orchestration for query: '{query}'")
    
    final_results = []
    
    # Change to project root for execution if currently in orchestrator dir
    # But usually we run from root. We will assume we are in 'price_comparison_bot' root or the parent of 'orchestrator'
    base_dir = os.getcwd()
    
    for scraper in SCRAPERS:
        name = scraper["name"]
        script = scraper["script"] # Relative to current dir?
        output_file = scraper["output"]
        
        # Check if script exists
        if not os.path.exists(script):
            log.error(f"Scraper script not found: {script}")
            continue

        log.info(f"Running scraper: {name}")
        
        try:
            # Run scraper as subprocess
            cmd = [sys.executable, script, query]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
            
            if result.returncode != 0:
                log.error(f"{name} scraper failed with code {result.returncode}")
                log.error(f"Stderr: {result.stderr}")
                # Continue strictly as per rules
            else:
                log.info(f"{name} scraper completed successfully")
            
            # Read output (Always try to read, even if returncode != 0, sometimes they dump data before crashing?)
            # Actually safe to try reading if file exists.
            
            data = load_json(output_file)
            if not data:
                log.warning(f"No output found for {name}")
                continue
                
            # Extract products list
            products = []
            if isinstance(data, dict):
                if "products" in data:
                    products = data["products"]
                elif "all_products" in data:
                    products = data["all_products"]
            elif isinstance(data, list):
                products = data
            
            log.info(f"{name} returned {len(products)} products")
            
            if not products:
                continue

            # Normalized for matcher
            # Note: We pass raw dictionary because matcher uses 'title' and 'price' if available
            # But creating a normalized copy for display is good.
            # Matcher expects a list of dicts.
            
            normalized_list = [normalize_product(p, name) for p in products]
            
            # Match Logic
            best_match = matcher.match_product(normalized_list, query)
            
            if best_match:
                log.info(f"Match found for {name}: {best_match['title']} - {best_match['price']}")
                final_results.append(best_match)
            else:
                log.warning(f"No matching product found for {name}")
            
            # Cooldown between scrapers to avoid detection
            log.info(f"Cooldown: waiting 5 seconds before next scraper...")
            time.sleep(5)
                
        except Exception as e:
            log.exception(f"Unexpected error running {name}: {e}")
            
    # Price Comparison across sites
    if final_results:
        # Sort by price
        def get_price(p):
            try:
                return float(p['price'])
            except:
                return float('inf')
                
        final_results.sort(key=get_price)
        
        # Mark cheapest
        cheapest = final_results[0]
        cheapest["recommended"] = True
        log.info(f"Recommended Product: {cheapest['title']} from {cheapest['site']} at {cheapest['price']}")
        
        # Save combined results
        exporter.export_results(final_results, output_dir="data")
        
    else:
        log.warning("No results collected from any scraper.")
        # Ensure we write empty results so UI doesn't crash reading old data
        exporter.export_results([], output_dir="data")
        
    return final_results

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "iphone 17"
    run_orchestrator(q)
