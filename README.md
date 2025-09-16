# 💰 Smart Interactive Price Tracker

## 🚀 Overview

This project evolves the automated price tracker into a full-stack, interactive web application. Instead of a backend-only script, this is a user-facing tool built with Streamlit that allows users to add, tag, and monitor product prices from various e-commerce sites in real-time.

It demonstrates a more complete skill set, including frontend development, user interaction, and more complex database management. This project fulfills a key promise on my professional CV with a more advanced, product-focused implementation.

## ✨ Features

* **Interactive UI:** A clean, user-friendly interface built with Streamlit for adding and viewing products.
* **Dynamic Scraping:** Users can paste any product URL to track it instantly.
* **Smart Scraping Logic:** The backend attempts to find prices and titles from multiple common e-commerce site structures (e.g., Amazon, Flipkart).
* **Tagging System:** Users can add custom tags to products for easy organization and filtering (e.g., "gifts," "electronics").
* **Persistent Storage:** All tracked products and their historical prices are stored in a robust PostgreSQL database.
* **Live Price Display:** The dashboard shows the most recently recorded price for every tracked item.

## 🛠️ Tech Stack

* **Language:** Python
* **Web Framework:** Streamlit
* **Libraries:** `requests`, `BeautifulSoup4`, `psycopg2-binary`
* **Database:** PostgreSQL (hosted on a service like Supabase)

## ⚙️ How to Deploy

1.  **Clone the repository.**
2.  **Get a free PostgreSQL database** from a provider like Supabase.
3.  **Push the repository** to your public GitHub account.
4.  **Deploy on Streamlit Community Cloud:**
    * Connect your GitHub account.
    * Select the repository.
    * In `Advanced settings > Secrets`, paste your PostgreSQL connection credentials in the required TOML format. For example:
        ```toml
        [postgres]
        host = "db.xxxxxxxx.supabase.co"
        port = "5432"
        dbname = "postgres"
        user = "postgres"
        password = "YOUR_PASSWORD"
        ```
5.  Click **Deploy!**