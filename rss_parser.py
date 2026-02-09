import feedparser
import requests
from datetime import datetime
from typing import List, Dict
from config import RSS_FEEDS, MONITORED_STOCKS

class RSSParser:
    """Parse RSS feeds from financial news sources"""
    
    def __init__(self):
        self.feeds = RSS_FEEDS
        self.stocks = MONITORED_STOCKS
        self.parsed_articles = []
    
    def fetch_feeds(self) -> List[Dict]:
        """Fetch and parse all RSS feeds"""
        articles = []
        
        for source_name, feed_url in self.feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Get last 10 entries
                    article = {
                        'source': source_name,
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', '')[:200],  # First 200 chars
                        'content': entry.get('content', [{}])[0].get('value', ''),
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"Error fetching {source_name}: {str(e)}")
                continue
        
        return articles
    
    def filter_by_stocks(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles related to monitored stocks"""
        filtered = []
        
        for article in articles:
            title = article['title'].upper()
            summary = article['summary'].upper()
            
            for stock in self.stocks:
                if stock in title or stock in summary:
                    article['matched_stock'] = stock
                    filtered.append(article)
                    break
        
        return filtered
    
    def get_latest_news(self) -> List[Dict]:
        """Get latest news for monitored stocks"""
        all_articles = self.fetch_feeds()
        filtered_articles = self.filter_by_stocks(all_articles)
        return filtered_articles

# Test
if __name__ == "__main__":
    parser = RSSParser()
    news = parser.get_latest_news()
    
    print(f"Found {len(news)} relevant articles\n")
    for article in news[:5]:
        print(f"Stock: {article['matched_stock']}")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print("---")