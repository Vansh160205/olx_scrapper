# OLX Car Cover Scraper

Scrapes search results from **OLX India** for the query _car cover_ and saves them to CSV and JSON.

> ⚠️ For demo/educational use only. Review OLX Terms of Service and robots.txt before scraping. Respect rate limits.

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Scrape first 3 pages and write to out/olx_car_covers.csv and .json
python olx_scraper.py --query "car cover" --pages 3 --out out/olx_car_covers
```

## Output
- `out/olx_car_covers.csv`
- `out/olx_car_covers.json`

Columns: `title, price, location, posted, url`

## GitHub steps

```bash
git init
git add .
git commit -m "Add OLX car cover scraper"
git branch -M main
git remote add origin https://github.com/<your-username>/olx-car-cover-scraper.git
git push -u origin main
```

## Notes
- OLX markup can change; selectors are written to be resilient, but not guaranteed.
- If you face blocking (429/403), reduce pages, increase `--delay`.
