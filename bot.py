import logging
import feedparser
from time import sleep
from bs4 import BeautifulSoup
from pyrogram import Client
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from info import LOG_CHANNEL, check_interval, API_ID, API_HASH, BOT_TOKEN, feed_urls, max_instances

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Initialize the bot client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store previously sent news titles to avoid duplicates
sent_titles = set()

# Default image URL if no image is found
DEFAULT_IMAGE_URL = "https://iili.io/2gWQbBR.jpg"

# Function to validate configuration
def validate_config():
    logging.info("Validating configuration...")
    required_vars = ["LOG_CHANNEL", "check_interval", "API_ID", "API_HASH", "BOT_TOKEN", "feed_urls", "max_instances"]
    missing_vars = [var for var in required_vars if var not in globals() or not globals()[var]]
    if missing_vars:
        raise ValueError(f"Missing required configuration variables: {', '.join(missing_vars)}")
    logging.info("Configuration validated successfully.")

# Function to extract image URL from feed entry
def get_image_url(entry):
    image_url = None

    # Check for media:content
    if "media_content" in entry:
        image_url = entry.media_content[0].get("url")
    # Check for media:thumbnail
    elif "media_thumbnail" in entry:
        image_url = entry.media_thumbnail[0].get("url")
    # Check for enclosure
    elif "enclosures" in entry and entry.enclosures:
        image_url = entry.enclosures[0].get("url")

    # If no image is found, check inside the description for an <img> tag
    if not image_url and "description" in entry:
        description_soup = BeautifulSoup(entry["description"], "html.parser")
        img_tag = description_soup.find("img")
        if img_tag:
            image_url = img_tag.get("src")

    # If the image URL doesn't end with a valid extension, append '.jpg'
    if image_url and not image_url.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_url += '.jpg'

    # Fallback to default image if no image is found
    return image_url if image_url else DEFAULT_IMAGE_URL

# Function to clean and format the description
def get_clean_description(entry, title):
    description_tag = entry.get("description", None)
    if description_tag:
        # Use BeautifulSoup to clean HTML tags from the description
        soup = BeautifulSoup(description_tag, "html.parser")
        description = soup.get_text(strip=True)
    else:
        description = "."

    # If the description is the same as the title, return None
    if description.strip() == title.strip():
        return None

    # Escape special characters for Telegram's HTML parse mode
    return description.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# Function to fetch and send news articles
def fetch_and_send():
    try:
        # Split and iterate over all feed URLs
        feeds = [url.strip() for url in feed_urls.split("|") if url.strip()]
        for feed_url in feeds:
            logging.info(f"Fetching news from {feed_url}...")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logging.warning(f"No articles found in {feed_url}.")
                continue

            for entry in feed.entries[:1]:  # Get the last 5 articles
                title = entry.get("title", "No Title")
                description = get_clean_description(entry, title)
                image_url = get_image_url(entry)

                if title in sent_titles:
                    logging.info(f"Skipping duplicate article: {title}")
                    continue

                try:
                    # Send the message with the image
                    if description:
                        app.send_photo(
                            LOG_CHANNEL,
                            photo=image_url,
                            caption=f"<b>{title}</b>\n\n<b>{description}</b>"
                        )
                    else:
                        app.send_photo(
                            LOG_CHANNEL,
                            photo=image_url,
                            caption=f"<b>{title}</b>"
                        )
                    logging.info(f"Sent news: {title}")
                    sent_titles.add(title)
                    sleep(60)  # Delay of 1 minute between each message
                except FloodWait as e:
                    logging.warning(f"FloodWait triggered: Sleeping for {e.x} seconds.")
                    sleep(e.x)

    except Exception as e:
        logging.error(f"Error occurred: {e}")

# Schedule the function to run at the defined interval
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_send, 'interval', seconds=check_interval, max_instances=max_instances)
    scheduler.start()
    logging.info("Scheduler started successfully.")

# Main function to run the bot
if __name__ == "__main__":
    try:
        validate_config()
        start_scheduler()
        logging.info("Bot is starting...")
        app.run()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
        BackgroundScheduler().shutdown()
