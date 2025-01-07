from os import environ
import os

API_ID = int(os.getenv("api_id", ))
API_HASH = os.getenv("api_hash", "")
BOT_TOKEN = os.getenv("bot_token", "")
OWNER_ID = int(environ.get("OWNER_ID", ""))
LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "-1001784714143")  # Telegram Channel ID where the bot is added and have write permission. You can use group ID too.
check_interval = int(os.environ.get("INTERVAL", 20))   # Check Interval in seconds.
max_instances = int(environ.get("MAX_INSTANCES", 3))
feed_urls = os.getenv("feed_urls", "https://www.thehindu.com/news/national/?service=rss|https://www.dnaindia.com/feeds/india.xml")

