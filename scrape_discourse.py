import os
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# --- USER CONFIGURATION ---
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_URL = "/c/courses/tds-kb/34"
SESSION_COOKIE = "7X4c6I2D2GZ3iNDOqQv8iB47kG2pEJAAWGpqOtwdvo35zPmcfBKKcPIkPxrgChXrESP1c6EFzTW0yzF7lZB4ZeNi1rqhvwXN8SqNvSI%2Fv5aBxHHu7Yk1fGUjt%2BUi4SYs%2Bs4AFt1h%2FxbVD%2FAZOFzzY9ayFnBAR8QM%2F8cdXmIbnoaXysAzkHqDr8%2FqAAq6dW7QWTRdMgA9mLA%2BIbdLDKgyP3XU5qk1ouquUN15sh86OVg0ldSzuxlES4NREDQpbrAX%2BUOynpy5dTzHOcJ2QkMRkfu1NGtwljE36VA%2FBP5wrWMmHPOr4Jo7KfuWFtbyPE8g--xYF6Nthn66yTUw4c--Zi8TtMEODF%2FPMRx6dIvlfg%3D%3D"  # Replace with your '_t' value
OUTPUT_DIR = "tds_pages_json"
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 4, 14)
HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- SETUP ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

session = requests.Session()
session.cookies.set("_t", SESSION_COOKIE, domain="discourse.onlinedegree.iitm.ac.in")
session.headers.update(HEADERS)

# --- FUNCTIONS ---
def get_all_topic_urls():
    print("Fetching topic list...")
    topic_urls = set()
    page = 0
    while True:
        url = f"{BASE_URL}{CATEGORY_URL}.json?page={page}"
        resp = session.get(url)
        if resp.status_code != 200:
            print(f"Failed to fetch page {page}: {resp.status_code}")
            break

        data = resp.json()
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break

        for topic in topics:
            created_at = datetime.strptime(topic["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
            if START_DATE <= created_at <= END_DATE:
                topic_urls.add(urljoin(BASE_URL, f"/t/{topic['slug']}/{topic['id']}"))

        page += 1
    print(f"Collected {len(topic_urls)} topics.")
    return topic_urls

def scrape_topic(url):
    print(f"Scraping topic: {url}")
    resp = session.get(url + ".json")
    if resp.status_code != 200:
        print(f"Failed to load topic JSON: {url}")
        return

    data = resp.json()
    topic_data = {
        "topic_id": data["id"],
        "title": data["title"].strip(),
        "url": url,
        "posts": []
    }

    for post in data["post_stream"]["posts"]:
        created_at = datetime.strptime(post["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if not (START_DATE <= created_at <= END_DATE):
            continue

        plain_text = BeautifulSoup(post["cooked"], "html.parser").get_text(separator="\n").strip()

        post_entry = {
            "post_id": post["id"],
            "author": post["username"],
            "created_at": created_at.isoformat(),
            "content": plain_text
        }
        topic_data["posts"].append(post_entry)

    if topic_data["posts"]:
        filename = os.path.join(OUTPUT_DIR, f"{topic_data['topic_id']}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(topic_data, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON: {filename}")

# --- MAIN ---
def main():
    topic_urls = get_all_topic_urls()
    for url in topic_urls:
        scrape_topic(url)

if __name__ == "__main__":
    main()
