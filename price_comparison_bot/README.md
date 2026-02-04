# 🤖 Price Comparison Bot

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

A professional, multi-platform e-commerce price comparison tool designed to extract, normalize, and compare product prices across **Amazon, Flipkart, Reliance Digital, and Croma**.

This project features both a **Robust Orchestrator** for managing concurrent scrapers and a **Modern Interactive Web Interface** (built with Streamlit) for instant price matching.

---

## 🌟 Key Features

### 🖥️ Interactive Web Dashboard
- **Unified Search**: Compare prices across 4 major retailers with a single query.
- **Smart Matching Logic**: Automatically identifies the "Best Choice" based on price and availability.
- **Visual List View**: Clean, card-based interface with product images and details.
- **Cross-Site Fallbacks**: Smart image filling ensures no product looks broken.
- **Instant Export**: Download comparison reports in **JSON**, **CSV**, or **Excel** formats vertically.

### ⚙️ advanced Scraping Engine
- **Multi-Site Architecture**: Dedicated scrapers for Amazon, Flipkart, Reliance, and Croma.
- **Manual Driver Control**: Bypasses corruption issues using a stable, fast local ChromeDriver.
- **Anti-Detection**: Built-in human behavior simulation (scroll, random sleep) to avoid bot detection.
- **Orchestration Layer**: Manages parallel execution and failure handling for all scrapers.
- **Resilient Logging**: Centralized logging system (`logs/scraper.log`) for execution tracking.

---

## 📥 Output Data

The tool extracts and normalizes the following fields for every search:
- 📝 **Product Title**
- 💰 **Current Price** (Normalized to INR)
- 🏪 **Source Website** (Amazon/Flipkart/etc.)
- 🔗 **Direct Product URL**
- 🖼️ **Product Image**
- ⭐ **Rating** (Where available)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Google Chrome Browser

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/price_comparison_bot.git
    cd price_comparison_bot
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup ChromeDriver**
    - Download ChromeDriver matching your Chrome version.
    - Extract to `C:\chromedriver`.
    *(Or update the path in scraper files if stored elsewhere)*

### Usage

#### Option A: Interactive Dashboard (Recommended)
Launch the visual interface in your browser:
```bash
streamlit run app.py
```

#### Option B: Headless CLI Orchestrator
Run the backend logic directly:
```bash
python orchestrator/runner.py "iPhone 15 Pro"
```

---

## 📁 Project Structure

```text
├── app.py                  # 🎨 Streamlit Web Application Entry Point
├── requirements.txt        # 📦 Project Dependencies
├── logs/                   # 📝 Centralized Runtime Logs
│   └── scraper.log
├── data/                   # 📊 Generated Reports (JSON/CSV)
├── orchestrator/           # 🧠 Core Logic
│   └── runner.py           #    - Manages scraper execution & merging
├── scrapers/               # 🕷️ Individual Site Scrapers
│   ├── amazon_scraper.py
│   ├── flipkart_scraper.py
│   ├── reliance_scraper.py
│   └── croma_scraper.py
└── utils/                  # 🛠️ Helper Utilities
    ├── matcher.py          #    - Fuzzy matching logic
    └── exporter.py         #    - Data export handlers
```

---

## ⚠️ Ethical Considerations

This tool is designed for **educational purposes** and **personal portfolio demonstration**. 
- It respects target sites by implementing delays between requests.
- Users are responsible for adhering to each platform's `robots.txt` policy and Terms of Service.

---

## 👤 Author

**Aryan Prajapati**
*Python Developer • Automation Engineer • Full Stack Enthusiast*

[![GitHub](https://img.shields.io/badge/GitHub-AryanPrajapati9456-181717?style=flat&logo=github)](https://github.com/AryanPrajapati9456)

---

### 📝 License
This project is open-source and available for usage under the MIT License.
