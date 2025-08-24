import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

# https://ethglobal.com/showcase?page=434
BASE_URL = "https://ethglobal.com"
START_PAGE = 1
END_PAGE = 434
CSV_FILE = "ethglobal_projects.csv"
DELAY_EVERY = 10  # every N pages
DELAY_SECONDS = 2  # seconds delay
RATE_LIMIT_DELAY = 60  # seconds on HTTP 429

def extract_projects_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    projects = []
    for a_tag in soup.find_all("a", class_="block border-2 border-black rounded overflow-hidden relative"):
        name_tag = a_tag.find("h2", class_="text-2xl")
        desc_tag = a_tag.find("p")
        link = a_tag.get("href")
        if name_tag and desc_tag and link:
            projects.append({
                "name": name_tag.text.strip(),
                "description": desc_tag.text.strip(),
                "url": BASE_URL + link
            })
    return projects

# Create CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["name", "description", "url"])
    df.to_csv(CSV_FILE, index=False)

headers = {"User-Agent": "Mozilla/5.0"}

for page in range(START_PAGE, END_PAGE + 1):
    url = f"{BASE_URL}/showcase?page={page}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            print(f"⚠️ Rate limit reached on page {page}. Waiting {RATE_LIMIT_DELAY} seconds...")
            time.sleep(RATE_LIMIT_DELAY)
            continue
        response.raise_for_status()
        projects = extract_projects_from_page(response.text)

        if projects:
            df = pd.DataFrame(projects)
            df.to_csv(CSV_FILE, mode="a", header=False, index=False)

        print(f"✅ Page {page} processed: {len(projects)} projects.")
        if page % DELAY_EVERY == 0:
            time.sleep(DELAY_SECONDS)
        else:
            time.sleep(1)
    except Exception as e:
        print(f"❌ Error on page {page}: {e}")

print("✅ Crawling complete.")

# Remove sequential duplicate rows (based on name + description + url)
try:
    df = pd.read_csv(CSV_FILE)
    df_dedup = df.loc[~(df.shift(1) == df).all(axis=1)].reset_index(drop=True)
    removed = len(df) - len(df_dedup)
    if removed > 0:
        df_dedup.to_csv(CSV_FILE, index=False)
        print(f"🧹 Removed {removed} sequential duplicate rows.")
    else:
        print("✅ No sequential duplicates found.")
except Exception as e:
    print(f"⚠️ Error while deduplicating the final CSV: {e}")
