# 🤖 Ultimate Price Comparison Suite

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium)
![API](https://img.shields.io/badge/API-Hybrid-purple?style=for-the-badge)

**Forget manual tab switching.** This project is a professional-grade reconnaissance tool that unifies the fragmeneted e-commerce landscape into a single, powerful dashboard. 

It doesn't just "search" — it intelligently orchestrates a fleet of specialized bots to scout **Amazon, Flipkart, Reliance Digital, and Croma** simultaneously. By combining advanced browser automation with reverse-engineered internal APIs, it delivers a real-time market snapshot that empowers users to find the absolute best deal in seconds.

---

## 🚀 Key Technical Features

### 🧠 Hybrid Scraping Architecture
We don't rely on a one-size-fits-all approach. Each scraper is custom-engineered for its target:
- **Selenium Stealth Bots (Amazon, Flipkart, Reliance)**: 
  - Mimics human behavior with random scrolling, mouse movements, and typing delays.
  - Bypasses sophisticated anti-bot systems (like Akamai/Distil) using a manual ChromeDriver setup that avoids common WebDriver fingerprints.
- **Direct API Reverse-Engineering (Croma)**: 
  - bypasses the browser entirely to talk directly to Croma's backend servers.
  - **Result:** Blazing fast data extraction (milliseconds vs seconds) with 100% accuracy.

### 🖥️ Modern Command Center
The Streamlit-based UI offers a premium experience:
- **Instant Visual Comparison**: Product cards are aligned side-by-side for easy decision making.
- **Intelligent Fallback System**: If a scraper fails to get an image (common on Reliance), the system automatically "borrows" the correct product image from another successful source (like Croma) to keep the UI pristine.
- **Data Export**: One-click generation of JSON, CSV, or Excel reports for offline analysis.

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
