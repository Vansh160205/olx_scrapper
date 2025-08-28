#!/usr/bin/env python3
"""
OLX Car Cover Scraper (Playwright version)
------------------------------------------
Scrapes results from: https://www.olx.in/items/q-car-cover
Outputs CSV and JSON with fields: title, price, location, url

Usage:
  python olx_scraper.py --query "car cover" --pages 3 --out out/olx_car_covers
"""

import argparse
import csv
import json
import os
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Optional
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


@dataclass
class Listing:
    title: str
    price: Optional[str]
    location: Optional[str]
    url: str


def fetch_html(url: str, page) -> str:
    """Fetch rendered HTML using Playwright."""
    page.goto(url, timeout=100000, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)  # wait 5 sec for JS to finish
    return page.content()


def parse_listings(html: str) -> List[Listing]:
    """Extract listings from rendered HTML."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    for card in soup.select("li._1DNjI"):   # OLX listing cards
        a_tag = card.find("a")
        if not a_tag:
            continue

        url = a_tag.get("href")
        if url and not url.startswith("http"):
            url = "https://www.olx.in" + url

        title = card.get_text(" ", strip=True).split("\n")[0] or "N/A"

        # Try price and location
        price_el = card.select_one("span[data-aut-id='itemPrice']")
        price = price_el.get_text(strip=True) if price_el else None

        loc_el = card.select_one("span[data-aut-id='item-location']")
        location = loc_el.get_text(strip=True) if loc_el else None

        listings.append(Listing(title=title, price=price, location=location, url=url))

    return listings


def save_results(listings: List[Listing], out_prefix: str) -> None:
    os.makedirs(os.path.dirname(out_prefix) or ".", exist_ok=True)

    with open(f"{out_prefix}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "location", "url"])
        writer.writeheader()
        for l in listings:
            writer.writerow(asdict(l))

    with open(f"{out_prefix}.json", "w", encoding="utf-8") as f:
        json.dump([asdict(l) for l in listings], f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(listings)} listings to {out_prefix}.csv and {out_prefix}.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="car cover")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--delay", type=float, default=2.0)
    ap.add_argument("--out", default="out/olx_car_covers")
    args = ap.parse_args()

    results = []
    query_slug = f"q-{quote_plus(args.query.replace(' ', '-'))}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headful for OLX
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))
        page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.olx.in/"
        })

        for page_num in range(1, args.pages + 1):
            url = f"https://www.olx.in/items/{query_slug}?page={page_num}"
            print(f"🔍 Fetching: {url}")
            try:
                html = fetch_html(url, page)
                listings = parse_listings(html)
                print(f"   → Found {len(listings)} listings on page {page_num}")
                results.extend(listings)
            except Exception as e:
                print(f"⚠️ Failed to fetch page {page_num}: {e}")
            time.sleep(args.delay + random.uniform(0, 0.5))

        browser.close()

    # Deduplicate by URL
    unique = {l.url: l for l in results}
    save_results(list(unique.values()), args.out)


if __name__ == "__main__":
    main()
