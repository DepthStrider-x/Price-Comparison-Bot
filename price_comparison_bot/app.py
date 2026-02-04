import streamlit as st
import subprocess
import sys
import json
import os
import pandas as pd
import time

# Page Config
st.set_page_config(page_title="Price Comparison Bot", layout="wide", page_icon="🤖")

# ========================
# CUSTOM CSS
# ========================
st.markdown("""
<style>
    /* Global Font & Background */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
    }
    
    /* Search Box Centering */
    div[data-testid="stTextInput"] {
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Product Card (List View) */
    .product-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.2s;
        border: 1px solid #eef2f6;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.1);
    }
    
    /* Image Styling */
    .product-img {
        height: 120px;
        width: 100%;
        object-fit: contain;
        border-radius: 8px;
    }
    
    /* Site Badge */
    .site-badge {
        font-size: 0.8em;
        padding: 4px 8px;
        border-radius: 4px;
        background-color: #f1f3f5;
        color: #495057;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    /* Price Styling */
    .price-tag {
        font-size: 1.4em;
        font-weight: 700;
        color: #2b8a3e;
    }
    
    /* Recommended Badge */
    .recommended-badge {
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5253 100%);
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: bold;
        position: absolute;
        top: -10px;
        right: -10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Hero Section */
    .hero-box {
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 20px;
        margin-bottom: 40px;
        color: #1a1a1a;
    }
    .hero-title {
        font-size: 3em;
        font-weight: 800;
        margin-bottom: 15px;
    }
    .hero-subtitle {
        font-size: 1.2em;
        color: #444;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# HEADER & SEARCH
# ========================

col1, col2, col3 = st.columns([1, 2, 1])

# Initial State Check
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# ========================
# LOGIC
# ========================

# Search Input (Always visible at top if searched, or inside hero if not)
if st.session_state.search_performed:
    st.markdown("<h2 style='text-align: center;'>🤖 Price Comparison Bot</h2>", unsafe_allow_html=True)
    query = st.text_input("", placeholder="Search for a product (e.g., iPhone 17)", key="search_bar_top")
else:
    # Hero Section for Empty State
    st.markdown("""
    <div class="hero-box">
        <div class="hero-title">Find the Best Deal. Instantly.</div>
        <div class="hero-subtitle">Compare prices across Amazon, Flipkart, Reliance, and Croma in one click.</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        query = st.text_input("Product Name", placeholder="e.g. iPhone 17 Pro", label_visibility="collapsed")
        search_pressed = st.button("🔍 Find Best Price", use_container_width=True, type="primary")

# Interaction Handler
if query and (st.session_state.search_performed or (not st.session_state.search_performed and 'search_pressed' in locals() and search_pressed)):
    
    st.session_state.search_performed = True
    
    # Progress UI
    progress_col1, progress_col2 = st.columns([1, 10])
    with progress_col1:
        spinner = st.spinner("")
    with progress_col2:
        status_text = st.empty()
        
    status_text.markdown("#### 🚀 Scouring the web for the best deals...")
    
    # Run Orchestrator
    cmd = [sys.executable, "orchestrator/runner.py", query]
    
    # Run script
    # We use a placeholder to simulate "working" UI since subprocess blocks
    try:
        with st.status("Searching stores...", expanded=True) as status:
            st.write("🔎 Connecting to Amazon...")
            time.sleep(0.5)
            st.write("🔎 Pinging Flipkart...")
            time.sleep(0.5)
            st.write("🔎 Checking Reliance & Croma...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode != 0:
                status.update(label="❌ Failed to fetch prices", state="error")
                st.error("Orchestration failed.")
                with st.expander("Error Log"):
                    st.code(result.stderr)
            else:
                status.update(label="✅ Search Complete!", state="complete")
        
        # Load Results
        json_path = "data/combined_results.json"
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
            
            if not data:
                st.warning("⚠️ No matching products found. Try a more specific keyword.")
                # Show trending/examples if empty
            else:
                st.markdown("### 🏷️ Comparison Results")
                st.write("")
                
                # Find a fallback image from any result that has one
                fallback_image = None
                for d in data:
                    if d.get("image") and d.get("image").startswith("http"):
                        fallback_image = d.get("image")
                        break
                
                # LIST VIEW LAYOUT
                for item in data:
                    is_recommended = item.get("recommended", False)
                    card_border = "2px solid #2b8a3e" if is_recommended else "1px solid #eef2f6"
                    bg_color = "#f4fcf5" if is_recommended else "white"
                    
                    # Create container for list item
                    with st.container():
                        # We use cols to create the "list item" layout
                        c_img, c_details, c_price = st.columns([1.5, 3.5, 1.5], gap="medium")
                        
                        # --- Image Column ---
                        with c_img:
                            img_url = item.get("image")
                            # Use fallback if current image is missing/invalid
                            if not (img_url and img_url.startswith("http")) and fallback_image:
                                img_url = fallback_image
                            
                            if img_url and img_url.startswith("http"):
                                st.image(img_url, use_container_width=True)
                            else:
                                st.markdown("🖼️ No Image")
                        
                        # --- Details Column ---
                        with c_details:
                            if is_recommended:
                                st.markdown("<span style='color: #2b8a3e; font-weight: bold;'>🏆 CHEAPEST OPTION</span>", unsafe_allow_html=True)
                            
                            st.markdown(f"#### {item.get('title')}")
                            st.markdown(f"<span class='site-badge'>{item.get('site')}</span>", unsafe_allow_html=True)
                            
                        
                        # --- Price Column ---
                        with c_price:
                            price = item.get("price")
                            st.markdown(f"<div class='price-tag'>₹{price}</div>", unsafe_allow_html=True)
                            st.link_button("View Deal ↗", item.get("url"), type="primary" if is_recommended else "secondary", use_container_width=True)
                        
                        st.divider()

                # Downloads Section
                st.markdown("### 📥 Export Data")
                dl1, dl2, dl3 = st.columns(3)
                
                with open("data/combined_results.json", "rb") as f:
                    dl1.download_button("📄 Download JSON", f, "results.json", "application/json", use_container_width=True)
                    
                if os.path.exists("data/results.csv"):
                    with open("data/results.csv", "rb") as f:
                        dl2.download_button("📊 Download CSV", f, "results.csv", "text/csv", use_container_width=True)
                        
    except Exception as e:
        st.error(f"Critical Error: {e}")

else:
    # Footer / Info when no search
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.info("🛒 **Amazon**")
    c2.info("🛍️ **Flipkart**")
    c3.info("🔌 **Reliance/Croma**")
