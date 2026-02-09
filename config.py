import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

# Stock Codes to Monitor (IDX - Indonesian Stock Exchange)
MONITORED_STOCKS = [
    'BBCA',  # Bank Central Asia
    'BMRI',  # Bank Mandiri
    'ASII',  # Astra International
    'UNVR',  # Unilever Indonesia
    'TLKM',  # Telkom
]

# RSS Feed URLs
RSS_FEEDS = {
    'CNBC Indonesia': 'https://www.cnbcindonesia.com/feed',
    'CNN Indonesia': 'https://www.cnnindonesia.com/feed',
    'IDX': 'https://www.idx.co.id/feed',
}

# Update interval in seconds (60 = 1 minute, 300 = 5 minutes)
UPDATE_INTERVAL = 300

# Sentiment threshold (-1 to 1)
SENTIMENT_POSITIVE_THRESHOLD = 0.1
SENTIMENT_NEGATIVE_THRESHOLD = -0.1