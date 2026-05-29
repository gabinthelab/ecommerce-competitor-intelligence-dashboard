import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import json


def extract_price_number(price_text):
    """Extract a number from price text like '$29.99' or '₱1,299'."""
    if not price_text:
        return None

    matches = re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", str(price_text))

    if matches:
        return float(matches[0].replace(",", ""))

    return None


def clean_text(value):
    """Clean text safely."""
    if not value:
        return None

    return " ".join(value.get_text(" ", strip=True).split())


def scrape_json_ld_products(soup, url):
    """
    Tries to scrape product data from structured JSON-LD.
    Many ecommerce sites use this for Google product listings.
    """

    products = []

    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

            items = data if isinstance(data, list) else [data]

            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    name = item.get("name")
                    description = item.get("description")

                    offers = item.get("offers", {})
                    price = None

                    if isinstance(offers, dict):
                        price = offers.get("price")

                    products.append({
                        "product_name": name,
                        "price_raw": price,
                        "price": extract_price_number(price),
                        "description": description,
                        "source_url": url,
                        "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

        except Exception:
            continue

    return products


def scrape_with_selectors(
    soup,
    url,
    card_selector,
    name_selector,
    price_selector,
    description_selector=None
):
    """Scrapes products using user-provided CSS selectors."""

    product_cards = soup.select(card_selector)

    products = []

    for card in product_cards:
        name_element = card.select_one(name_selector)
        price_element = card.select_one(price_selector)

        description_element = None
        if description_selector:
            description_element = card.select_one(description_selector)

        product_name = clean_text(name_element)
        price_raw = clean_text(price_element)
        description = clean_text(description_element)

        products.append({
            "product_name": product_name,
            "price_raw": price_raw,
            "price": extract_price_number(price_raw),
            "description": description,
            "source_url": url,
            "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    return products


def scrape_auto(soup, url):
    """
    Simple fallback scraper.
    It looks for common product-card patterns.
    This will not work on every website, but it helps for portfolio use.
    """

    possible_card_selectors = [
        "div.thumbnail",
        ".product",
        ".product-card",
        ".product-item",
        ".grid-product",
        ".card",
        "li.product"
    ]

    possible_name_selectors = [
        "a.title",
        ".product-title",
        ".product-name",
        "h2",
        "h3",
        "a"
    ]

    possible_price_selectors = [
        "h4.price",
        ".price",
        ".product-price",
        ".money",
        "[class*='price']"
    ]

    for card_selector in possible_card_selectors:
        cards = soup.select(card_selector)

        if not cards:
            continue

        products = []

        for card in cards:
            name = None
            price = None

            for name_selector in possible_name_selectors:
                name = card.select_one(name_selector)
                if name:
                    break

            for price_selector in possible_price_selectors:
                price = card.select_one(price_selector)
                if price:
                    break

            product_name = clean_text(name)
            price_raw = clean_text(price)

            if product_name or price_raw:
                products.append({
                    "product_name": product_name,
                    "price_raw": price_raw,
                    "price": extract_price_number(price_raw),
                    "description": None,
                    "source_url": url,
                    "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        if products:
            return products

    return []


def scrape_from_url(
    url,
    card_selector=None,
    name_selector=None,
    price_selector=None,
    description_selector=None,
    save_path="products.csv"
):
    """Main scraper function used by the Streamlit app."""

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200:
        raise Exception(f"Could not access website. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    products = []

    # 1. If user provided selectors, use them
    if card_selector and name_selector and price_selector:
        products = scrape_with_selectors(
            soup=soup,
            url=url,
            card_selector=card_selector,
            name_selector=name_selector,
            price_selector=price_selector,
            description_selector=description_selector
        )

    # 2. Try JSON-LD product data
    if not products:
        products = scrape_json_ld_products(soup, url)

    # 3. Try auto-detect fallback
    if not products:
        products = scrape_auto(soup, url)

    if not products:
        raise Exception(
            "No product data found. This site may be dynamic, blocked, or may need custom CSS selectors."
        )

    df = pd.DataFrame(products)

    df.to_csv(save_path, index=False)

    return df