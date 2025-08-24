import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

INPUT_CSV = "ethglobal_projects.csv"
OUTPUT_FOLDER = "project_details"
DELIMITER = "|"

DELAY_EVERY = 20
DELAY_SECONDS = 10
RATE_LIMIT_DELAY_SECONDS = 3600

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def clean(text):
    return text.replace("\n", " ").replace("|", "-").replace(";", ",").replace("\t", " ").strip()

def extract_project_details(url):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 429:
            print("⚠️ Rate limit reached. Waiting 60 seconds...")
            time.sleep(RATE_LIMIT_DELAY_SECONDS)
            return extract_project_details(url)

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        header = soup.find("header")
        name = clean(header.find("h1").text) if header and header.find("h1") else "Not specified"
        short_desc = clean(header.find("p").text) if header and header.find("p") else "Not specified"

        buttons = header.find_all("a") if header else []
        live_demo_url = "Not specified"
        source_code_url = "Not specified"
        for a in buttons:
            if "live demo" in a.text.lower():
                live_demo_url = a.get("href", "Not specified")
            elif "source code" in a.text.lower():
                source_code_url = a.get("href", "Not specified")

        def get_section_text_by_h3(soup, title):
            h3 = soup.find("h3", string=lambda s: s and title.lower() in s.lower())
            if h3:
                container = h3.find_next("div")
                if container:
                    paragraphs = container.find_all("p")
                    return clean(" ".join(p.text for p in paragraphs))
            return "Not specified"

        project_desc = get_section_text_by_h3(soup, "Project Description")
        how_its_made = get_section_text_by_h3(soup, "How it's Made")

        def get_created_at_url(soup):
            h3 = soup.find("h3", string=lambda s: s and "created at" in s.lower())
            if h3:
                a = h3.find_next("a", href=True)
                if a:
                    return a["href"]
            return "Not specified"

        created_at_link = get_created_at_url(soup)

        awards = []
        winner_section = soup.find("h3", string=lambda s: s and "winner of" in s.lower())
        if winner_section:
            award_container = winner_section.find_next_sibling("div")
            if award_container:
                h4s = award_container.find_all("h4")
                awards = [clean(h4.text) for h4 in h4s]

        return {
            "name": name,
            "short_description": short_desc,
            "live_demo_url": live_demo_url,
            "source_code_url": source_code_url,
            "project_description": project_desc,
            "how_its_made": how_its_made,
            "created_at": created_at_link,
            "awards": ", ".join(awards) if awards else "Not specified",
            "project_url": url
        }

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None


existing_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".csv") and f[:4].isdigit()]
start_index = max([int(f[:4]) for f in existing_files], default=0)
print(f"🔄 Resuming from index {start_index + 1}...")

df = pd.read_csv(INPUT_CSV)

for idx, row in df.iloc[start_index:].iterrows():
    project_url = row.get("url")
    if not isinstance(project_url, str):
        continue

    details = extract_project_details(project_url)
    if details:
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in details['name'].replace(' ', '_'))
        output_path = os.path.join(OUTPUT_FOLDER, f"{idx+1:04d}_{safe_name}.csv")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(DELIMITER.join(details.keys()) + "\n")
                f.write(DELIMITER.join(details.values()) + "\n")
            print(f"✅ Saved: {output_path}")
        except Exception as e:
            error_log = os.path.join(OUTPUT_FOLDER, "error_log.txt")
            with open(error_log, "a", encoding="utf-8") as err:
                err.write(f"{output_path} | Error: {str(e)}\n")
            print(f"❌ Error saving file {output_path}: {e}")

    if (idx + 1) % DELAY_EVERY == 0:
        time.sleep(DELAY_SECONDS)
    else:
        time.sleep(1)
