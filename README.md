# 🤖 Ultimate Price Comparison Suite

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium)
![API](https://img.shields.io/badge/API-Hybrid-purple?style=for-the-badge)

# 🔍 Unified E-Commerce Price Comparison Dashboard

Forget manual tab switching.  
This project unifies multiple Indian e-commerce platforms into a single comparison dashboard, allowing users to quickly evaluate prices, availability, and product details across stores.

Rather than relying on a one-size-fits-all scraping approach, the system applies site-specific data collection strategies to improve reliability, speed, and resilience when interacting with real-world e-commerce websites such as **Amazon, Flipkart, Reliance Digital, and Croma**.

---



https://github.com/user-attachments/assets/4aa69d11-46c4-43fa-b3b6-1af6390acacd




## 🚀 Key Technical Features

---

### 🧠 Hybrid Data Collection Architecture

Different platforms require different techniques. This project adapts accordingly:

- **Browser Automation (Amazon, Flipkart, Reliance Digital)**
  - Selenium-based automation with realistic interaction patterns (scrolling, navigation delays, user-like behavior)
  - Designed to reduce failures caused by dynamic content loading and basic bot-detection systems
  - Focuses on stability and repeatability rather than aggressive scraping

- **Direct HTTP Requests (Croma)**
  - Uses publicly accessible backend endpoints identified via browser network inspection
  - Bypasses browser overhead for faster data extraction
  - Improves consistency for pricing and availability data

> This hybrid architecture mirrors how production-grade scraping systems are typically designed:  
> **selecting the right tool per platform instead of forcing a single solution everywhere.**

---

### 🖥️ Interactive Comparison Dashboard

The Streamlit-based UI prioritizes clarity and fast decision-making:

- **Side-by-Side Product Comparison**
  - Prices, ratings, and availability aligned in a single view

- **Graceful Data Fallbacks**
  - Automatically reuses verified data (such as product images) from another source when a field is missing

- **Exportable Results**
  - One-click export to **CSV**, **JSON**, or **Excel** formats for offline analysis

---

## 📂 Project Structure

This monorepo is organized into specialized modules:

### 1. ⚡ Main Application (`price_comparison_bot/`)
The central brain of the operation.
- **`app.py`**: The Streamlit frontend that visualizes the data.
- **`orchestrator/runner.py`**: The subprocess manager that launches all scrapers in parallel.
- **`scrapers/`**: The integrated versions of all bot scripts.

### 2. 🧪 Standalone Scrapers
Specialized labs for testing individual sites.
- **`Amazon_Scraper/`**: Dedicated Selenium bot for Amazon.
- **`Flipkart_scraper/`**: Advanced bot with risk-detection bypass logic.
- **`Croma_Scraper/`**: The high-speed API implementation.
- **`Reliance_digital/`**: Browser automation for Reliance trends.

---

## ⚙️ Customization Guide

### How to Change Product Limits
By default, the bots fetch the **top 5 relevant products** per site to ensure relevance. You can scale this up easily:

1.  **For Flipkart & Amazon:**
    - Open `price_comparison_bot/scrapers/flipkart_scraper.py` (Line 24)
    - Open `price_comparison_bot/scrapers/amazon_scraper.py` (Line 26)
    - Change `MAX_PRODUCTS = 5` to your desired number (e.g., `10`).

2.  **For Croma (API):**
    - Open `price_comparison_bot/scrapers/croma_scraper.py` (Line 15)
    - Change `MAX_PRODUCTS = 5` to `20` or more (APIs are fast!)

---

## 🛠️ Quick Start

### Prerequisites
1. **Python 3.10+**
2. **Google Chrome Browser**
3. **ChromeDriver**: Must be installed manually at `C:\chromedriver\chromedriver-win64\chromedriver.exe` to bypass auto-update corruption issues.

### Installation

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/DepthStrider-x/Price-Comparison-Bot.git
   cd Price-Comparison-Bot
   ```

2. **Install Common Dependencies:**
   ```bash
   pip install selenium streamlit pandas openpyxl requests
   ```

3. **Run the Main Bot:**
   ```bash
   cd price_comparison_bot
   streamlit run app.py
   ```

---

## ⚠️ Disclaimer
These tools are for **educational and research purposes only**. Please respect the `robots.txt` and Terms of Service of all websites.

---

## 👤 Author
**Aryan Prajapati**
