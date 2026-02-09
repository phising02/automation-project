from textblob import TextBlob
from typing import Dict, Tuple
from config import SENTIMENT_POSITIVE_THRESHOLD, SENTIMENT_NEGATIVE_THRESHOLD

class SentimentAnalyzer:
    """Analyze sentiment of news articles"""
    
    def __init__(self):
        self.positive_keywords = [
            'naik', 'meningkat', 'bagus', 'profit', 'untung', 'strong',
            'gain', 'rise', 'bullish', 'buy', 'rally', 'surge', 'jump'
        ]
        
        self.negative_keywords = [
            'turun', 'menurun', 'rugi', 'loss', 'bearish', 'sell',
            'decline', 'drop', 'crash', 'negative', 'weak', 'fall'
        ]
    
    def analyze_text(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text
        Returns: (polarity_score, sentiment_label)
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            
            # Custom keyword checking for financial news
            text_lower = text.lower()
            positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
            
            # Adjust polarity based on keywords
            adjusted_polarity = polarity
            if positive_count > negative_count:
                adjusted_polarity = max(polarity, 0.2)
            elif negative_count > positive_count:
                adjusted_polarity = min(polarity, -0.2)
            
            # Determine sentiment label
            if adjusted_polarity > SENTIMENT_POSITIVE_THRESHOLD:
                label = "POSITIVE 📈"
            elif adjusted_polarity < SENTIMENT_NEGATIVE_THRESHOLD:
                label = "NEGATIVE 📉"
            else:
                label = "NEUTRAL ➡️"
            
            return adjusted_polarity, label
        
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            return 0.0, "NEUTRAL ➡️"
    
    def analyze_article(self, article: Dict) -> Dict:
        """Analyze sentiment of an article"""
        text = f"{article['title']} {article['summary']}"
        polarity, label = self.analyze_text(text)
        
        article['sentiment_score'] = round(polarity, 2)
        article['sentiment_label'] = label
        
        return article

# Test
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    test_text = "Saham BBCA naik signifikan hari ini dengan profit yang besar"
    score, label = analyzer.analyze_text(test_text)
    print(f"Text: {test_text}")
    print(f"Sentiment: {label} (Score: {score})")