from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
    page.goto("https://www.olx.in/items/q-car-cover?page=1", timeout=100000, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)  # let JS finish
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")
cards = soup.select("li._1DNjI")

print(f"Found {len(cards)} listings")
for card in cards[:5]:
    title = card.get_text(" ", strip=True).split("\n")[0]
    link = card.find("a").get("href")
    if not link.startswith("http"):
        link = "https://www.olx.in" + link
    print(title, "→", link)
