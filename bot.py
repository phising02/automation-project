import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, UPDATE_INTERVAL
from rss_parser import RSSParser
from sentiment_analyzer import SentimentAnalyzer

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class StockNewsBot:
    """Telegram bot for stock news and sentiment analysis"""
    
    def __init__(self):
        self.rss_parser = RSSParser()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.last_sent_articles = set()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        welcome_message = """
🤖 *Selamat Datang di Stock News Bot!*

Bot ini memberikan news dan sentiment analysis untuk saham Indonesia secara real-time.

*Perintah yang tersedia:*
/start - Tampilkan pesan ini
/news - Dapatkan berita terbaru
/stocks - Lihat daftar saham yang dipantau
/sentiment - Lihat analisis sentimen terbaru
/help - Bantuan
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def get_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get latest news"""
        await update.message.reply_text("⏳ Mengambil berita terbaru...")
        
        try:
            articles = self.rss_parser.get_latest_news()
            
            if not articles:
                await update.message.reply_text("📰 Belum ada berita terbaru untuk saham yang dipantau")
                return
            
            # Show first 5 articles
            for article in articles[:5]:
                analyzed = self.sentiment_analyzer.analyze_article(article)
                
                message = f"""
📰 *{analyzed['matched_stock']}*
*Judul:* {analyzed['title']}
*Sumber:* {analyzed['source']}
*Sentimen:* {analyzed['sentiment_label']} ({analyzed['sentiment_score']})
*Link:* [{analyzed['source']}]({analyzed['link']})
                """
                await update.message.reply_text(message, parse_mode='Markdown')
                await asyncio.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            logger.error(f"Error getting news: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def get_stocks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List monitored stocks"""
        stocks_list = ", ".join(self.rss_parser.stocks)
        message = f"📊 *Saham yang Dipantau:*\n\n{stocks_list}"
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def get_sentiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get sentiment analysis"""
        try:
            articles = self.rss_parser.get_latest_news()
            
            if not articles:
                await update.message.reply_text("📊 Belum ada data untuk analisis sentimen")
                return
            
            # Analyze all articles
            analyzed_articles = [
                self.sentiment_analyzer.analyze_article(article)
                for article in articles
            ]
            
            # Group by sentiment
            positive = [a for a in analyzed_articles if '📈' in a['sentiment_label']]
            negative = [a for a in analyzed_articles if '📉' in a['sentiment_label']]
            neutral = [a for a in analyzed_articles if '➡️' in a['sentiment_label']]
            
            message = f"""
📊 *Analisis Sentimen Pasar*
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 *Positif:* {len(positive)} artikel
📉 *Negatif:* {len(negative)} artikel
➡️ *Netral:* {len(neutral)} artikel

*Top Positive:*
"""
            for article in positive[:3]:
                message += f"\n• {article['matched_stock']}: {article['title'][:50]}..."
            
            await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error getting sentiment: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
*📖 Bantuan Bot*

*Fitur Utama:*
✅ Monitoring berita saham real-time
✅ Analisis sentimen otomatis
✅ Alert untuk saham tertentu
✅ Tracking harga dan tren

*Perintah:*
/start - Mulai bot
/news - Berita terbaru
/stocks - Daftar saham
/sentiment - Analisis sentimen
/help - Bantuan ini

*Cara Menggunakan:*
1. Tambahkan bot ke chat/group
2. Gunakan perintah di atas
3. Bot akan mengirim berita dan analisis secara berkala

*Saham yang Dipantau:*
BBCA, BMRI, ASII, UNVR, TLKM
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def auto_send_news(self, context: ContextTypes.DEFAULT_TYPE):
        """Send news automatically at intervals"""
        try:
            articles = self.rss_parser.get_latest_news()
            
            for article in articles:
                article_id = f"{article['source']}-{article['title']}"
                
                # Only send if not sent before
                if article_id not in self.last_sent_articles:
                    analyzed = self.sentiment_analyzer.analyze_article(article)
                    
                    message = f"""
🔔 *Berita Baru!*

*{analyzed['matched_stock']}*
{analyzed['title']}

*Sentimen:* {analyzed['sentiment_label']} ({analyzed['sentiment_score']})
*Sumber:* {analyzed['source']}
                    """
                    
                    try:
                        await context.bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=message,
                            parse_mode='Markdown'
                        )
                        self.last_sent_articles.add(article_id)
                    except Exception as e:
                        logger.error(f"Error sending message: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in auto_send_news: {str(e)}")

def main():
    """Start the bot"""
    bot = StockNewsBot()
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("news", bot.get_news))
    application.add_handler(CommandHandler("stocks", bot.get_stocks))
    application.add_handler(CommandHandler("sentiment", bot.get_sentiment))
    application.add_handler(CommandHandler("help", bot.help_command))
    
    # Add job for auto-sending news
    application.job_queue.run_repeating(
        bot.auto_send_news,
        interval=UPDATE_INTERVAL,
        first=10
    )
    
    # Start bot
    logger.info("Bot starting...")
    print("🤖 Bot is running... Press Ctrl+C to stop")
    application.run_polling()

if __name__ == '__main__':
    main()