import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Price Tracker", page_icon="💰", layout="wide")

# --- DATABASE CONNECTION (using Streamlit Secrets) ---
def get_db_connection():
    conn = psycopg2.connect(**st.secrets["postgres"])
    return conn

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    # Table for tracked products (the master list)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracked_products (
            id SERIAL PRIMARY KEY,
            product_url TEXT UNIQUE NOT NULL,
            product_name TEXT,
            tags TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    # Table for historical prices (the log)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES tracked_products(id) ON DELETE CASCADE,
            price NUMERIC(10, 2) NOT NULL,
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- WEB SCRAPING ---
def scrape_product_details(product_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Scrape Title ---
        title = soup.find("span", {"id": "productTitle"})
        if not title:
             title = soup.find("span", {"class": "B_NuCI"}) # Flipkart
        product_name = title.get_text(strip=True) if title else "Name not found"


        # --- Scrape Price ---
        price_selectors = [
            {"tag": "span", "attrs": {"class": "a-price-whole"}}, # Amazon
            {"tag": "div", "attrs": {"class": "_30jeq3 _16Jk6d"}}, # Flipkart
        ]
        price_text = None
        for selector in price_selectors:
            price_element = soup.find(selector["tag"], selector["attrs"])
            if price_element:
                price_text = price_element.get_text(strip=True).replace(',', '').replace('₹', '').split('.')[0]
                break
        
        price = float(price_text) if price_text else None
        
        return {"name": product_name, "price": price}

    except Exception as e:
        st.error(f"Failed to scrape {product_url}: {e}")
        return None

# --- DATABASE OPERATIONS ---
def add_product_to_track(url, tags):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        details = scrape_product_details(url)
        if details and details["price"] is not None:
            # Add to master list
            cur.execute(
                "INSERT INTO tracked_products (product_url, product_name, tags) VALUES (%s, %s, %s) RETURNING id",
                (url, details["name"], tags)
            )
            product_id = cur.fetchone()[0]
            
            # Add first price to history
            cur.execute(
                "INSERT INTO price_history (product_id, price) VALUES (%s, %s)",
                (product_id, details["price"])
            )
            conn.commit()
            st.success(f"Successfully started tracking: {details['name']}")
        else:
            st.error("Could not retrieve product details or price. Please check the URL.")
    except psycopg2.IntegrityError:
        st.warning("This product is already being tracked.")
        conn.rollback()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_tracked_products():
    conn = get_db_connection()
    cur = conn.cursor()
    # Get latest price for each product
    cur.execute("""
        SELECT DISTINCT ON (tp.id)
            tp.id, tp.product_url, tp.product_name, tp.tags, ph.price, ph.scraped_at
        FROM tracked_products tp
        LEFT JOIN price_history ph ON tp.id = ph.product_id
        ORDER BY tp.id, ph.scraped_at DESC;
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

# --- UI RENDER ---
st.title("💰 Smart E-commerce Price Tracker")

# Initialize database on first run
setup_database()

st.header("Track a New Product")
with st.form("track_form", clear_on_submit=True):
    new_url = st.text_input("Product URL", placeholder="Paste the full link to the product page here...")
    tag_input = st.text_input("Tags (comma-separated)", placeholder="e.g., electronics, gift, phone")
    submitted = st.form_submit_button("Track Product")

    if submitted and new_url:
        tags_list = [tag.strip() for tag in tag_input.split(',')] if tag_input else []
        add_product_to_track(new_url, tags_list)

st.markdown("---")
st.header("Your Tracked Products")

tracked_products = get_tracked_products()

if not tracked_products:
    st.info("You are not tracking any products yet. Add a URL above to get started!")
else:
    for prod in tracked_products:
        prod_id, url, name, tags, price, last_scraped = prod
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(name)
            st.caption(f"URL: {url}")
            if tags:
                st.write("Tags: " + " | ".join(f"`{tag}`" for tag in tags))
        with col2:
            st.metric(label="Last Recorded Price", value=f"₹{price:,.2f}" if price else "N/A")
            st.caption(f"Last checked: {last_scraped.strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")
