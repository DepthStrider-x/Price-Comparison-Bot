# 🤖 Ultimate Price Comparison Suite

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium)

This repository contains a complete suite of web scraping tools for Indian e-commerce platforms. It is organized into **Standalone Scrapers** for individual site targeted scraping and a **Main Integrated Bot** that orchestrates them all into a powerful price comparison engine.

---

## 📂 Project Structure

This monorepo is divided into the following modules:

### 1. 🚀 Main Application (`price_comparison_bot/`)
**The Flagship Tool.** This is the integrated solution that runs all scrapers in parallel, matches products, comparing prices, and presents a beautiful Web UI.

- **Features:** Streamlit UI, Fuzzy Product Matching, Excel/JSON Exports.
- **Usage:**
  ```bash
  cd price_comparison_bot
  streamlit run app.py
  ```
- **Documentation:** See `price_comparison_bot/README.md` for full details.

### 2. 🕷️ Standalone Scrapers
Individual folders containing specialized scripts for scraping specific websites. These are useful if you only need data from one source or want to study the logic for a specific site.

- **`Amazon_Scraper/`**: Dedicated tool for extracting Amazon product data.
- **`Flipkart_scraper/`**: Specialized scraper for Flipkart with anti-bot detection handling.
- **`Reliance_digital/`**: Scraper for Reliance Digital electronics.
- **`Croma_Scraper/`**: Scraper for Croma Retail.

---

## 🛠️ Quick Start

### Prerequisites
1. **Python 3.10+**
2. **Google Chrome Browser**
3. **ChromeDriver**: Must be installed manually at `C:\chromedriver\chromedriver-win64\chromedriver.exe` (or update paths in scripts).

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
