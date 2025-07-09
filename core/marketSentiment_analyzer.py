import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import date
from core.db_handler import get_signal  # Your existing client
from urllib.parse import quote_plus

analyzer = SentimentIntensityAnalyzer()

def fetch_google_news_headlines(symbol, max_articles=20):
    query = quote_plus(f"{symbol} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(rss_url)
    headlines = [entry.title for entry in feed.entries[:max_articles]]
    return headlines

def analyze_sentiment(headlines):
    if not headlines:
        return "neutral"

    scores = [analyzer.polarity_scores(t)["compound"] for t in headlines]
    avg_score = sum(scores) / len(scores)

    if avg_score > 0.2:
        return "positive"
    elif avg_score < -0.2:
        return "negative"
    return "neutral"

def get_or_cache_sentiment(symbol, signal_type="LONG_TERM_BUY"):
    today = str(date.today())

    # Step 1: Check if sentiment already cached
    result = get_signal(symbol, today, signal_type)

    if result.data:
        sentiment = result.data[0].get("market_sentiment", "neutral")
        print(f"[📦] Cached sentiment for {symbol}: {sentiment}")
        return sentiment

    # Step 2: Fetch and analyze
    headlines = fetch_google_news_headlines(symbol)
    sentiment = analyze_sentiment(headlines)
    print(f"[📰] Fetched sentiment for {symbol}: {sentiment}")
    return sentiment
