import requests
import json
import os
from datetime import datetime, timezone

SUBREDDITS = ["sidehustle", "entrepreneur", "smallbusiness", "passive_income", "beermoney"]
LIMIT = 25
DATA_DIR = "data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_posts(subreddit: str, limit: int = 25) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    children = resp.json()["data"]["children"]
    return [
        {
            "id": p["data"]["id"],
            "title": p["data"]["title"],
            "score": p["data"]["score"],
            "url": p["data"]["url"],
            "permalink": "https://reddit.com" + p["data"]["permalink"],
            "num_comments": p["data"]["num_comments"],
            "created_utc": p["data"]["created_utc"],
            "author": p["data"]["author"],
            "selftext": p["data"]["selftext"][:500] if p["data"]["selftext"] else "",
        }
        for p in children
    ]


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
