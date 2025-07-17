import feedparser
import random
import schedule
import time
import threading
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from ollama_client import paraphrase_article
from image_utils import get_image_url

BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Заменить!
CHANNEL_ID = '@your_channel_name'      # Заменить!
SOURCE_FILE = 'sources.txt'

def load_sources():
    with open(SOURCE_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def get_random_article():
    sources = load_sources()
    random.shuffle(sources)
    for source in sources:
        feed = feedparser.parse(source)
        if feed.entries:
            random.shuffle(feed.entries)
            for entry in feed.entries:
                image_url = None
                if 'media_content' in entry:
                    image_url = entry.media_content[0].get('url')
                elif 'media_thumbnail' in entry:
                    image_url = entry.media_thumbnail[0].get('url')
                elif 'enclosures' in entry and entry.enclosures:
                    image_url = entry.enclosures[0].get('href')

                return {
                    "title": entry.title,
                    "summary": entry.get("summary", ""),
                    "link": entry.link,
                    "image_url": image_url
                }
    return None

async def post_news(bot):
    entry = get_random_article()
    if not entry:
        await bot.send_message(chat_id=CHANNEL_ID, text="🥲 Не удалось получить новость.")
        return

    raw_text = f"{entry['title']}

{entry['summary']}"
    funny_post = paraphrase_article(raw_text)
    caption = f"{funny_post[:1024]}

[Читать подробнее]({entry['link']})"

    image_url = entry["image_url"] or get_image_url()
    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption, parse_mode="Markdown")

def start_scheduler(bot):
    def job():
        asyncio.run(post_news(bot))
    schedule.every(30).minutes.do(job)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    t = threading.Thread(target=run_scheduler)
    t.daemon = True
    t.start()

async def manual_post(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Публикую новость вручную...")
    await post_news(context.bot)

async def add_source(update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи ссылку на RSS после команды.")
        return
    new_url = context.args[0]
    with open(SOURCE_FILE, 'a') as f:
        f.write(f"{new_url}
")
    await update.message.reply_text(f"✅ Источник добавлен: {new_url}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("post", manual_post))
    app.add_handler(CommandHandler("addsource", add_source))
    start_scheduler(app.bot)
    print("🤖 Бот запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()