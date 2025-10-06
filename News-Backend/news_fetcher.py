import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datetime import datetime
from news_backend.models import NewsBase

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GNEWS_KEY = os.getenv("GNEWS_KEY")

def fetch_newsapi(query="technology"):
    print(f" Fetching news for: {query}")
    print(f" API key loaded: {bool(NEWS_API_KEY)}")
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"
    r = requests.get(url).json()
    return [
        {
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url"),
            "image": a.get("urlToImage"),  
            "publishedAt": a.get("publishedAt"),
            "source": {"name": a.get("source", {}).get("name", "NewsAPI")}
        }
        for a in r.get("articles", [])
    ]


def fetch_gnews(query="technology"):
    url = f"https://gnews.io/api/v4/search?q={query}&token={GNEWS_KEY}&lang=en"
    r = requests.get(url).json()
    return [
        {
            "title": a.get("title"),
            "description": a.get("description"),
            "url": a.get("url"),
            "image": a.get("image"),  
            "publishedAt": a.get("publishedAt"),
            "source": {"name": a.get("source", {}).get("name", "GNews")}
        }
        for a in r.get("articles", [])
    ]


def get_combined_news(query="technology"):
    results = []
    results.extend(fetch_newsapi(query))
    results.extend(fetch_gnews(query))
    return results

def save_news_to_db(db: Session, articles):
    for article in articles:
        # check duplicate by URL
        exists = db.query(NewsBase).filter(NewsBase.url == article["url"]).first()
        if not exists:
            # Convert publishedAt string → datetime
            published_at = None
            if article.get("publishedAt"):
                try:
                    published_at = datetime.fromisoformat(
                        article["publishedAt"].replace("Z", "+00:00")
                    )
                except Exception:
                    published_at = datetime.utcnow()  

            news_item = NewsBase(
                title=article["title"],
                source=article.get("source", {}).get("name", "Unknown"),
                publishedAt=published_at,
                url=article["url"],
                description=article.get("description"),
            )
            db.add(news_item)
    db.commit()

