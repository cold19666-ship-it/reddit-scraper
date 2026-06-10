import requests
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SUBREDDITS = ["sidehustle", "entrepreneur", "smallbusiness", "passive_income", "beermoney"]
LIMIT = 25
DATA_DIR = "data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}


def fetch_posts(subreddit: str, limit: int = 25) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/.rss?limit={limit}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)[:limit]

    posts = []
    for entry in entries:
        title = entry.find("atom:title", ns)
        link = entry.find("atom:link", ns)
        author = entry.find("atom:author/atom:name", ns)
        updated = entry.find("atom:updated", ns)
        content = entry.find("atom:content", ns)

        posts.append({
            "id": link.get("href", "") if link is not None else "",
            "title": title.text if title is not None else "",
            "score": 0,  # RSS doesn't include score
            "url": link.get("href", "") if link is not None else "",
            "permalink": link.get("href", "") if link is not None else "",
            "num_comments": 0,  # RSS doesn't include comments count
            "created_utc": updated.text if updated is not None else "",
            "author": author.text if author is not None else "unknown",
            "selftext": (content.text or "")[:500] if content is not None else "",
        })

    return posts


def save(subreddit: str, posts: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = f"{DATA_DIR}/{subreddit}_{today}.json"

    existing = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    existing_ids = {p["id"] for p in existing}
    new_posts = [p for p in posts if p["id"] not in existing_ids]
    all_posts = existing + new_posts

    with open(path, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)

    print(f"[{subreddit}] 新增 {len(new_posts)} 条，共 {len(all_posts)} 条 → {path}")


if __name__ == "__main__":
    for sub in SUBREDDITS:
        try:
            posts = fetch_posts(sub, LIMIT)
            save(sub, posts)
        except Exception as e:
            print(f"[{sub}] 失败: {e}")
            # Continue with next subreddit, don't fail the whole run
